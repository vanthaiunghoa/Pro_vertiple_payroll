# vertiple_payroll
Payroll Outsourcing : 38.76.11.162:5000/vertiple_payroll:v1.0.0
## Deployment guide:
### Vertiple Payroll Outsourcing:

1. Install Vertiple | Payroll (enthsquare_payroll)
2. Install Vertiple | Website (vr_website) with theme (Bootswatch)
3. Configure Multi Company (including the currency) 
4. Configure custom payslip report name
5. Set key report.url system parameter with value http://127.0.0.1:8069

### Vertiple Saas Model:

Clone the saas_dev branch into the volume that has been mounted to the production docker container
Now, to get rid of the filestore issue goto the master db and run this SQL query
```
DELETE FROM ir_attachment WHERE url LIKE '/web/content/%';
```
1. Once you are done with the above steps start upgrading the following modules/apps by logging in as Admin
2. Upgrade Vertiple | Payroll (enthsquare_payroll)
3. Install Enthsquare | HRMS (vertiple_employee)
4. Install Vertiple | Attendance-Payroll (vr_attendance_payroll)
5. Install Employee Checklist (employee_check_list)
