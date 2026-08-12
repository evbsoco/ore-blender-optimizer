import pulp

class OreBlenderOptimizer:
    """
    MILP-based ore blending optimizer.

    Optimization priorities:
        1. Minimize normalized Ni + Fe grade excess.
        2. Minimize selected WMT.

    Each pile is either:
        1 -> completely consumed
        0 -> not consumed.
    """

    def __init__(
        self,
        inventory,
        vessel,
        tolerance=1e-5,
    ):
        self.inventory = inventory
        self.vessel = vessel
        self.tolerance = tolerance

    # =========================================================
    # Helpers
    # =========================================================

    def _get_piles(self):
        """
        Return the piles available for optimization.

        Change this if your Inventory stores its piles
        under a different attribute.
        """
        return self.inventory.piles

    def _get_total_wmt(self, selected_piles):
        return sum(pile.wmt for pile in selected_piles)

    def _get_blended_grade(self, selected_piles, element):
        total_wmt = self._get_total_wmt(selected_piles)

        if total_wmt <= 0:
            raise ValueError("Cannot calculate blended grade with zero WMT.")

        return (
            sum(pile.wmt * getattr(pile, element) for pile in selected_piles) / total_wmt
        )

    def _get_grade_objective(self, selected_piles):
        """
        Normalized Ni + Fe excess.

        Ni and Fe are equally important.

        Example:

            Ni = 1.55
            Ni requirement = 1.50

            Ni excess =
                (1.55 - 1.50) / 1.50

        Same calculation for Fe.
        """

        ni = self._get_blended_grade(selected_piles, "ni")

        fe = self._get_blended_grade(selected_piles, "fe")

        ni_requirement = self.vessel.ni_spec
        fe_requirement = self.vessel.fe_spec

        ni_excess = ( (ni - ni_requirement) / ni_requirement )

        fe_excess = ( (fe - fe_requirement) / fe_requirement )

        return ni_excess + fe_excess

    # =========================================================
    # Primary optimization
    # =========================================================

    def _optimize_grade(self):
        """
        Primary optimization.

        Uses the Charnes-Cooper transformation to convert
        the fractional blended-grade objective into a MILP.

        Returns:
            selected_piles
            optimal_grade_objective
        """

        piles = self._get_piles()

        if not piles:
            raise ValueError("Inventory contains no piles.")

        capacity = self.vessel.capacity_target
        threshold = self.vessel.capacity_threshold

        maximum_wmt = ( capacity + threshold )

        ni_requirement = self.vessel.ni_spec
        fe_requirement = self.vessel.fe_spec

        # -----------------------------------------------------
        # Validate requirements
        # -----------------------------------------------------

        if capacity <= 0:
            raise ValueError( "Vessel capacity must be greater than zero." )

        if threshold < 0:
            raise ValueError( "Capacity threshold cannot be negative." )

        if ni_requirement <= 0:
            raise ValueError( "Ni requirement must be greater than zero." )

        if fe_requirement <= 0:
            raise ValueError( "Fe requirement must be greater than zero." )

        # -----------------------------------------------------
        # Charnes-Cooper bounds
        #
        # t = 1 / total_WMT
        # -----------------------------------------------------

        t_min = 1 / maximum_wmt
        t_max = 1 / capacity

        # -----------------------------------------------------
        # Create MILP
        # -----------------------------------------------------

        model = pulp.LpProblem( "Ore_Blending_Grade_Optimization", pulp.LpMinimize )

        # -----------------------------------------------------
        # Variables
        # -----------------------------------------------------

        # x_i = 1 if pile is consumed
        x = {
            pile.index: pulp.LpVariable(
                f"x_{pile.index}",
                cat=pulp.LpBinary
            )
            for pile in piles
        }

        # y_i = x_i * t
        y = {
            pile.index: pulp.LpVariable(
                f"y_{pile.index}",
                lowBound=0
            )
            for pile in piles
        }

        # t = 1 / total selected WMT
        t = pulp.LpVariable(
            "t",
            lowBound=t_min,
            upBound=t_max
        )

        # -----------------------------------------------------
        # Objective
        # -----------------------------------------------------

        objective = pulp.lpSum(
            pile.wmt
            * (
                (pile.ni - ni_requirement)
                / ni_requirement
                +
                (pile.fe - fe_requirement)
                / fe_requirement
            )
            * y[pile.index]
            for pile in piles
        )

        model += objective

        # -----------------------------------------------------
        # Normalization
        #
        # sum(W_i * y_i) = 1
        # -----------------------------------------------------

        model += (
            pulp.lpSum(
                pile.wmt * y[pile.index]
                for pile in piles
            )
            == 1,
            "Normalization"
        )

        # -----------------------------------------------------
        # Capacity
        #
        # t = 1 / W
        #
        # Since:
        #
        # capacity <= W <= maximum_wmt
        #
        # we have:
        #
        # 1 / maximum_wmt <= t <= 1 / capacity
        #
        # -----------------------------------------------------

        model += (
            t >= t_min,
            "Minimum_t"
        )

        model += (
            t <= t_max,
            "Maximum_t"
        )

        # -----------------------------------------------------
        # Ni requirement
        # -----------------------------------------------------

        model += (
            pulp.lpSum(
                pile.wmt
                * (pile.ni - ni_requirement)
                * y[pile.index]
                for pile in piles
            )
            >= 0,
            "Minimum_Ni"
        )

        # -----------------------------------------------------
        # Fe requirement
        # -----------------------------------------------------

        model += (
            pulp.lpSum(
                pile.wmt
                * (pile.fe - fe_requirement)
                * y[pile.index]
                for pile in piles
            )
            >= 0,
            "Minimum_Fe"
        )

        # -----------------------------------------------------
        # Linearization:
        #
        # y_i = x_i * t
        #
        # t_min <= t <= t_max
        #
        # -----------------------------------------------------

        for pile in piles:

            pile_id = pile.index

            # y_i <= t_max * x_i
            model += (
                y[pile_id]
                <= t_max * x[pile_id],
                f"Y_Upper_X_{pile_id}"
            )

            # y_i <= t
            model += (
                y[pile_id]
                <= t,
                f"Y_Upper_T_{pile_id}"
            )

            # y_i >= t - t_max(1 - x_i)
            model += (
                y[pile_id]
                >=
                t
                - t_max * (1 - x[pile_id]),
                f"Y_Lower_{pile_id}"
            )

        # -----------------------------------------------------
        # Solve
        # -----------------------------------------------------

        print("\nSolving primary grade optimization...")

        status = model.solve(
            pulp.PULP_CBC_CMD(
                msg=False
            )
        )

        if pulp.LpStatus[status] != "Optimal":

            raise RuntimeError(
                "Primary grade optimization failed. "
                f"Solver status: "
                f"{pulp.LpStatus[status]}"
            )

        # -----------------------------------------------------
        # Extract selected piles
        # -----------------------------------------------------

        selected_piles = [
            pile
            for pile in piles
            if pulp.value(x[pile.index]) > 0.5
        ]

        if not selected_piles:
            raise RuntimeError(
                "Solver returned an empty pile selection."
            )

        optimal_grade = pulp.value(
            model.objective
        )

        print(
            f"Primary grade optimization complete."
        )

        # Uncomment to check candidate piles
        # print("\nPRIMARY SOLUTION")

        # for pile in selected_piles:
        #     print(
        #         f"{pile.index} | "
        #         f"{pile.pile} | "
        #         f"WMT={pile.wmt} | "
        #         f"Ni={pile.ni} | "
        #         f"Fe={pile.fe}"
        #     )

        # print("Number of piles:", len(selected_piles))
        # print(
        #     "Total WMT:",
        #     sum(p.wmt for p in selected_piles)
        # )

        # print(
        #     f"Optimal normalized grade excess: "
        #     f"{optimal_grade:.10f}"
        # )

        return (
            selected_piles,
            optimal_grade
        )

    # =========================================================
    # Secondary optimization
    # =========================================================

    def _optimize_tonnage(
        self,
        optimal_grade,
    ):
        """
        Secondary optimization.

        Preserve the optimal grade solution within tolerance,
        then minimize total selected WMT.

        Since:

            t = 1 / WMT

        minimizing WMT is equivalent to maximizing t.
        """

        piles = self._get_piles()

        capacity = self.vessel.capacity_target
        threshold = self.vessel.capacity_threshold

        maximum_wmt = (
            capacity + threshold
        )

        ni_requirement = self.vessel.ni_spec
        fe_requirement = self.vessel.fe_spec

        t_min = 1 / maximum_wmt
        t_max = 1 / capacity

        model = pulp.LpProblem(
            "Ore_Blending_Tonnage_Optimization",
            pulp.LpMaximize
        )

        # -----------------------------------------------------
        # Variables
        # -----------------------------------------------------

        x = {
            pile.index: pulp.LpVariable(
                f"x_{pile.index}",
                cat=pulp.LpBinary
            )
            for pile in piles
        }

        y = {
            pile.index: pulp.LpVariable(
                f"y_{pile.index}",
                lowBound=0
            )
            for pile in piles
        }

        t = pulp.LpVariable(
            "t",
            lowBound=t_min,
            upBound=t_max
        )

        # -----------------------------------------------------
        # Secondary objective
        #
        # Maximize t
        #
        # equivalent to minimizing WMT
        # -----------------------------------------------------

        model += t

        # -----------------------------------------------------
        # Normalization
        # -----------------------------------------------------

        model += (
            pulp.lpSum(
                pile.wmt * y[pile.index]
                for pile in piles
            )
            == 1,
            "Normalization"
        )

        # -----------------------------------------------------
        # Preserve optimal grade
        #
        # grade_objective <= optimal_grade + tolerance
        # -----------------------------------------------------

        grade_expression = pulp.lpSum(
            pile.wmt
            * (
                (pile.ni - ni_requirement)
                / ni_requirement
                +
                (pile.fe - fe_requirement)
                / fe_requirement
            )
            * y[pile.index]
            for pile in piles
        )

        model += (
            grade_expression
            <= optimal_grade + self.tolerance,
            "Optimal_Grade"
        )

        # -----------------------------------------------------
        # Ni requirement
        # -----------------------------------------------------

        model += (
            pulp.lpSum(
                pile.wmt
                * (pile.ni - ni_requirement)
                * y[pile.index]
                for pile in piles
            )
            >= 0,
            "Minimum_Ni"
        )

        # -----------------------------------------------------
        # Fe requirement
        # -----------------------------------------------------

        model += (
            pulp.lpSum(
                pile.wmt
                * (pile.fe - fe_requirement)
                * y[pile.index]
                for pile in piles
            )
            >= 0,
            "Minimum_Fe"
        )

        # -----------------------------------------------------
        # t bounds
        # -----------------------------------------------------

        model += (
            t >= t_min,
            "Minimum_t"
        )

        model += (
            t <= t_max,
            "Maximum_t"
        )

        # -----------------------------------------------------
        # Linearization:
        #
        # y_i = x_i * t
        # -----------------------------------------------------

        for pile in piles:

            pile_id = pile.index

            model += (
                y[pile_id]
                <= t_max * x[pile_id],
                f"Y_Upper_X_{pile_id}"
            )

            model += (
                y[pile_id]
                <= t,
                f"Y_Upper_T_{pile_id}"
            )

            model += (
                y[pile_id]
                >=
                t
                - t_max * (1 - x[pile_id]),
                f"Y_Lower_{pile_id}"
            )

        # -----------------------------------------------------
        # Solve
        # -----------------------------------------------------

        # Uncomment to check candidate piles
        print(
            "\nSolving secondary tonnage optimization..."
        )

        # print("\nSECONDARY CANDIDATES")
        # print("Number of candidates:", len(piles))

        # for pile in piles:
        #     print(
        #         f"{pile.index} | "
        #         f"{pile.pile} | "
        #         f"WMT={pile.wmt} | "
        #         f"Ni={pile.ni} | "
        #         f"Fe={pile.fe}"
        #     )

        status = model.solve(
            pulp.PULP_CBC_CMD(
                msg=False
            )
        )

        # print("\nSECONDARY VARIABLES")

        # for pile in piles:
        #     var = x[pile.index]

        #     print(
        #         f"{pile.index} | "
        #         f"{pile.pile} | "
        #         f"WMT={pile.wmt} | "
        #         f"x={var.value()}"
        #     )

        if pulp.LpStatus[status] != "Optimal":

            raise RuntimeError(
                "Tonnage optimization failed. "
                f"Solver status: "
                f"{pulp.LpStatus[status]}"
            )

        selected_piles = [
            pile
            for pile in piles
            if pulp.value(x[pile.index]) > 0.5
        ]

        if not selected_piles:
            raise RuntimeError( "Secondary optimization returned an empty pile selection." )

        return selected_piles

    # =========================================================
    # Public solve method
    # =========================================================

    def solve(self):
        """
        Run the complete two-stage optimization.
        """

        # =====================================================
        # Stage 1
        #
        # Optimize grade
        # =====================================================

        (
            grade_solution,
            optimal_grade
        ) = self._optimize_grade()

        # =====================================================
        # Stage 2
        #
        # Optimize tonnage while preserving grade
        # =====================================================

        final_solution = self._optimize_tonnage(
            optimal_grade
        )

        # =====================================================
        # Calculate final results
        # =====================================================

        total_wmt = self._get_total_wmt(
            final_solution
        )

        blended_ni = self._get_blended_grade(
            final_solution,
            "ni"
        )

        blended_fe = self._get_blended_grade(
            final_solution,
            "fe"
        )

        final_grade_objective = (
            self._get_grade_objective(
                final_solution
            )
        )

        return {
            "selected_piles": final_solution,
            "total_wmt": total_wmt,
            "ni": blended_ni,
            "fe": blended_fe,
            "grade_objective": final_grade_objective,
            "initial_grade_solution": grade_solution,
        }