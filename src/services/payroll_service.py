"""Payroll management services."""


class PayrollService:
    """Handle payroll operations."""

    def __init__(self, db_adapter):
        self.db = db_adapter

    @staticmethod
    def calculate_gross(base_salary: float, allowances: float, overtime_hours: float, overtime_rate: float) -> float:
        return float(base_salary) + float(allowances) + (float(overtime_hours) * float(overtime_rate))

    @staticmethod
    def calculate_net(gross: float, deductions: float) -> float:
        return float(gross) - float(deductions)

    def add_payroll(self, employee_id: int, period_start: str, period_end: str,
                    base_salary: float, allowances: float = 0.0, deductions: float = 0.0,
                    overtime_hours: float = 0.0, overtime_rate: float = 0.0,
                    status: str = "Draft", paid_date: str = "") -> bool:
        gross = self.calculate_gross(base_salary, allowances, overtime_hours, overtime_rate)
        net = self.calculate_net(gross, deductions)
        return self.db.add_payroll(
            employee_id, period_start, period_end, base_salary, allowances, deductions,
            overtime_hours, overtime_rate, gross, net, status, paid_date
        )

    def get_all_payrolls(self) -> list:
        return self.db.get_all_payrolls()

    def get_payrolls_by_employee(self, employee_id: int) -> list:
        return self.db.get_payrolls_by_employee(employee_id)

    def update_payroll(self, payroll_id: int, **kwargs) -> bool:
        base_salary = kwargs.get("base_salary")
        allowances = kwargs.get("allowances")
        deductions = kwargs.get("deductions")
        overtime_hours = kwargs.get("overtime_hours")
        overtime_rate = kwargs.get("overtime_rate")

        if base_salary is not None or allowances is not None or deductions is not None or overtime_hours is not None or overtime_rate is not None:
            base_salary = base_salary if base_salary is not None else kwargs.get("_current_base", 0.0)
            allowances = allowances if allowances is not None else kwargs.get("_current_allowances", 0.0)
            deductions = deductions if deductions is not None else kwargs.get("_current_deductions", 0.0)
            overtime_hours = overtime_hours if overtime_hours is not None else kwargs.get("_current_overtime_hours", 0.0)
            overtime_rate = overtime_rate if overtime_rate is not None else kwargs.get("_current_overtime_rate", 0.0)
            gross = self.calculate_gross(base_salary, allowances, overtime_hours, overtime_rate)
            net = self.calculate_net(gross, deductions)
            kwargs["gross_pay"] = gross
            kwargs["net_pay"] = net

        kwargs.pop("_current_base", None)
        kwargs.pop("_current_allowances", None)
        kwargs.pop("_current_deductions", None)
        kwargs.pop("_current_overtime_hours", None)
        kwargs.pop("_current_overtime_rate", None)

        return self.db.update_payroll(payroll_id, **kwargs)

    def delete_payroll(self, payroll_id: int) -> bool:
        return self.db.delete_payroll(payroll_id)
