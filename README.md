## Asset Sync Manager - Backend
- This repository contains the backend code for the Asset Inventory Management system, a project aimed at centralizing information and tracking assets within an organization. The backend is built using Python Flask and utilizes PostgreSQL as the database. The project follows best practices and implements strict access controls to ensure that only authorized personnel, including Admins, Procurement Managers, and Finance, can access specific functionalities.

## Table of Contents
- Features
- Minimum Viable Product
- Technologies Used
- Getting Started
- API Endpoints
- Contributing
- License

## Features
1. User Authentication:

- Implements secure user authentication for authorized access.

2. User Roles:

- Classifies users into Admins, Procurement Managers, and regular Employees.
Data Access Controls:

- Grants the right to add, update, or remove data based on user classification.
Only Procurement Managers can review and approve asset requests.
Centralized Data Storage:

- All data is stored in a central PostgreSQL database.

3. Asset Management:

- Admins can add assets, including images and categories.
- Managers can allocate assets to employees.

4. Request Management:

- Users can request new assets or repairs through a user-friendly form.
- Managers can view all pending and completed requests.

## Minimum Viable Product

- The initial version focuses on allowing user authentication, classifying users, implementing data access controls, and centralizing data storage. It provides the ability to add, update, and remove assets, allocate assets to employees, and manage asset requests.

## Technologies Used
- Backend: Python Flask
- Database: PostgreSQL

## Getting Started
Clone the Repository:

bash
Copy code
git clone git@github.com:jankimutai/Asset-Sync-Manager-BackEnd.git
cd asset-inventory-management-backend
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Run the Application:

bash
Copy code
python3 app.py

## API Endpoints
- *Authentication:*
  - /api/auth/login - POST request to authenticate a user.
  - / - GET request for a welcome message.
  - /login - POST request for user login.
  - /manager_login - POST request for manager login.
  - /registration - POST request for user registration.
  - /session_user - GET request to check user session.
  - /logout - DELETE request for user logout.
  
- *User Management:*
  - /api/users - GET request to retrieve user information.

- *Asset Management:*
  - /api/assets - GET request to retrieve all assets.
  - /api/assets - POST request to add a new asset.
  - /api/assets/{asset_id} - GET request to get an asset by ID.
  - /api/assets/{asset_id} - PUT request to update an asset by ID.
  - /api/assets/{asset_id} - DELETE request to delete an asset by ID.
  - /api/assets/allocate/{asset_id} - POST request to allocate an asset to an employee.

- *Assignment Management:*
  - /api/user_assignments - GET request to get assignments for a user.
  - /api/assignments - GET request to get all assignments.
  - /api/assignments - POST request to create a new assignment.

- *Transaction Management:*
  - /api/transaction/{transaction_id} - GET request to get a transaction by ID.
  - /api/transactions - GET request to get all transactions.

- *Maintenance Management:*
  - /api/maintenances - GET request to get all maintenances.
  - /api/maintenances - POST request to create a new maintenance.
  - /api/maintenance/{maintenance_id} - GET request to get maintenance by ID.
 
- *Request Management:*
  - /api/request/{request_id} - GET request to get a request by ID.
  - /api/requests - GET request to get all requests.
  - /api/requests - POST request to create a new request.
  - /api/user_requests - GET request to get requests by User ID.

- *User Profile:*
  - /api/user/profile/{user_id} - GET request to get user profile by ID.
  - /api/user/profile/{user_id} - PUT request to update user profile by ID.


## Contributing
-We welcome contributions to the Asset Inventory Management backend! 

*Contributors*
1. Jan Kimutai
2. Anzal Abdinoor
3. Robert Njunge

## License
This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
