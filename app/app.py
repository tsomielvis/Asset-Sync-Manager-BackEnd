from flask_restful import Resource,reqparse
from psycopg2 import IntegrityError
from app.config import app,api,db
from flask import make_response,jsonify,request,session
from app.models import Asset, User, Assignment, Maintenance, Transaction, Requests
from datetime import datetime
from werkzeug.exceptions import NotFound
from flask_cors import cross_origin,CORS
from sqlalchemy import desc

class Home(Resource):
    def get(self):
        response =make_response(jsonify({"message":"Welcome to Asset-Sync-Manager-Backend"}), 200)
        return response
    
api.add_resource(Home,"/")
class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()

        if user:
            if user.authenticate(args['password']):
                if user.role == 'employee' or user.role == "Employee":
                    session["user_id"] = user.id
                    session.permanent = True
                    print(f"User ID set in session: {session['user_id']}")
                    return user.to_dict(), 201
                else:
                    return make_response(jsonify({'error': 'Insufficient privileges'}), 403)
            else:
                return make_response(jsonify({'error': 'Invalid password'}), 401)
        else:
            return make_response(jsonify({'error': 'Invalid username or insufficient privileges'}), 401)
api.add_resource(Login, "/login", endpoint="login")
class ManagerLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()

        if user:
            if user.authenticate(args['password']):
                if user.role == "Admin" or user.role == "Procurement" :
                    session["user_id"] = user.id
                    session.permanent = True
                    print(f"User ID set in session: {session['user_id']}")
                    return make_response(jsonify(user.to_dict()), 201)
                else:
                    return make_response(jsonify({'error': 'Insufficient privileges'}), 403)
            else:
                return make_response(jsonify({'error': 'Invalid password'}), 401)
        else:
            return make_response(jsonify({'error': 'Invalid username or insufficient privileges'}), 401)
api.add_resource(ManagerLogin, "/manager_login", endpoint="manager_login")
class Registration(Resource):
   def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('full_name', type=str, required=True, help='Full name is required')
        parser.add_argument('username', type=str, required=True, help='Username is required')
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        parser.add_argument('role', type=str, required=True, help='Role is required')
        parser.add_argument('department', type=str, required=True, help='Department is required')

        args = parser.parse_args()

        new_user = User(
            full_name=args['full_name'],
            username=args['username'],
            email=args['email'],
            role=args['role'],
            department=args['department']
        )

        new_user.password_hash = str(args.get('password'))

        try:
            db.session.add(new_user)
            db.session.commit()
            # session["user_id"]=new_user.id
            # session.permanent=True
            return make_response(jsonify({'message': 'User registered successfully'}), 201)
        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({'error': 'Username or email already exists'}), 409)

api.add_resource(Registration,"/registration",endpoint="registration")
class CheckUser(Resource):
    @cross_origin(supports_credentials=True)
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return jsonify(user.to_dict()),200
        else:
            return jsonify({"error": "user not in session:please signin/login"}), 401
api.add_resource(CheckUser,'/session_user',endpoint='session_user' )
class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id']=None
            return {"message": "User logged out successfully"}
        else:
            return {"error":"User must be logged in to logout"}
api.add_resource(Logout, '/logout', endpoint='logout')
class PasswordUpdateResource(Resource):
    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('password', type=str, required=True, help='Password is required')

        args = parser.parse_args()

        new_password = args['password']

        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}, 404))
        user.password_hash = new_password
        db.session.commit()

        return make_response(jsonify({'message': 'Password updated successfully'}), 200)
api.add_resource(PasswordUpdateResource, '/update_password',endpoint="/update_password")
class Assets(Resource):
    def get(self):
        assets = [asset.to_dict() for asset in Asset.query.order_by(desc(Asset.id)).all()]
        response= make_response(jsonify(assets), 200)
        return response
    def post(self):
        data = request.get_json()
        
        # Log the incoming data for debugging
        app.logger.debug(f"Incoming POST request data: {data}")

        new_asset = Asset(
            asset_name=data.get('assetName'),
            model=data.get('model'),
            image_url=data.get('imageUrl'),
            manufacturer=data.get('manufacturer'),
            date_purchased=data.get('datePurchased'),
            purchase_cost=data.get("purchaseCost"),
            status=data.get('status'),
            category=data.get('category'),
            serial_number=data.get('serialNumber')
        )

        try:
            db.session.add(new_asset)
            db.session.commit()
            return make_response(jsonify({'message': 'Asset created successfully'}), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 400)
api.add_resource(Assets,"/assets")
class AssetById(Resource):
    def get(self, asset_id):
        asset = Asset.query.filter_by(id=asset_id).first()

        if not asset:
            return make_response(jsonify({'error': 'Asset not found'}), 404)

        return make_response(jsonify(asset.to_dict()), 200)
    def put(self, asset_id):
        asset = Asset.query.filter_by(id=asset_id).first()
        data = request.get_json()

        asset.asset_name = data.get('asset_name', asset.asset_name)
        asset.model = data.get('model', asset.model)
        asset.image_url = data.get('image_url', asset.image_url)
        asset.manufacturer = data.get('manufacturer', asset.manufacturer)
        asset.date_purchased = datetime.strptime(data.get('date_purchased', asset.date_purchased), '%Y-%m-%d').date() if data.get('date_purchased') else None
        asset.added_on = datetime.strptime(data.get('added_on', asset.added_on), '%Y-%m-%d').date() if data.get('added_on') else None
        asset.purchase_cost=data.get("purchase_cost", asset.purchase_cost)
        asset.status = data.get('status', asset.status)
        asset.category = data.get('category', asset.category)
        asset.serial_number=data.get('serial_number',asset.serial_number)

        try:
            db.session.commit()
            return make_response(jsonify({'message': 'Asset updated successfully'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 400)

    def delete(self, asset_id):
        asset = Asset.query.filter_by(id=asset_id).first()

        try:
            db.session.delete(asset)
            db.session.commit()
            return make_response(jsonify({'message': 'Asset deleted successfully'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 400)

api.add_resource(AssetById,'/asset/<int:asset_id>')
class AssignmentById(Resource):
    def get(self, assignment_id):
        assignment = Assignment.query.filter_by(id=assignment_id).first()
        if not assignment:
            return make_response(jsonify({'message': 'Assignment not found'}), 404)

        return make_response(jsonify(assignment.to_dict()),200)

    def put(self, assignment_id):
        assignment = Assignment.query.filter_by(id=assignment_id).first()

        parser = reqparse.RequestParser()
        
        parser.add_argument('asset_id', type=int, help='Asset ID', required=True)
        parser.add_argument('user_id', type=int, help='User ID')
        parser.add_argument('assignment_date', type=str, help='Assignment date')
        parser.add_argument('return_date', type=str, help='Return date')
        args = parser.parse_args()

        if not assignment:
            return make_response(jsonify({'message': 'Assignment not found'}), 404)

        assignment.asset_id = args['asset_id']
        assignment.user_id = args['user_id']
        assignment.assignment_date = datetime.strptime(args['assignment_date'], '%Y-%m-%d').date() if args['assignment_date'] else None
        assignment.return_date = datetime.strptime(args['return_date'], '%Y-%m-%d').date() if args['return_date'] else None

        db.session.commit()

        return make_response(jsonify({'message': 'Assignment updated successfully'}, 201))

    def delete(self, assignment_id):
        assignment = Assignment.query.filter_by(id=assignment_id).first()
        if not assignment:
            return make_response(jsonify({'message': 'Assignment not found'}), 404)

        db.session.delete(assignment)
        db.session.commit()

        return make_response(jsonify({'message': 'Assignment deleted successfully'}), 204)
api.add_resource(AssignmentById, '/assignment/<int:assignment_id>')

class AssignmentListResource(Resource):
    def get(self):
        assignments = Assignment.query.order_by(desc(Assignment.asset_id)).all()

        if not assignments:
            return make_response(jsonify({'message': 'Assignments not found'}, 404))

        serialized_assignments = []

        for assignment in assignments:
            serialized_assignment = assignment.to_dict()
            serialized_assignment['full_name'] = assignment.name
            serialized_assignment['asset_name'] = assignment.asset_name
            serialized_assignments.append(serialized_assignment)

        return make_response(jsonify(serialized_assignments), 200)
    def post(self):

        parser = reqparse.RequestParser()

        parser.add_argument('asset_id', type=int, help='Asset ID', required=True)
        parser.add_argument('user_id', type=int, help='User ID')
        parser.add_argument('assignment_date', type=str, help='Assignment date')
        parser.add_argument('return_date', type=str, help='Return date')

        args = parser.parse_args()
        new_assignment = Assignment(
            asset_id=args['asset_id'],
            user_id=args['user_id'],
            assignment_date=datetime.strptime(args['assignment_date'], '%Y-%m-%d').date() if args['assignment_date'] else None,
            return_date= datetime.strptime(args['return_date'], '%Y-%m-%d').date() if args['return_date'] else None
        )

        db.session.add(new_assignment)
        db.session.commit()

        response_data = {'message': 'Assignment created successfully', 'assignment_id': new_assignment.id}
        return make_response(jsonify(response_data),201)
api.add_resource(AssignmentListResource, '/assignments')

class TransactionResource(Resource):
    def get(self, transaction_id):
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
        if not transaction:
            response = make_response(jsonify({'error': 'Transaction not found'}), 404)
            return response

        return make_response(jsonify(transaction.to_dict()), 200)

    def put(self, transaction_id):
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()

        parser = reqparse.RequestParser()
    
        parser.add_argument('asset_id', type=int, help='Asset ID', required=True)
        parser.add_argument('transaction_type', type=str, help='Transaction type', required=True)
        parser.add_argument('transaction_date', type=str, help='Transaction date')
        
        args = parser.parse_args()
        

        if not transaction:
            return make_response(jsonify({'error': 'Transaction not found'}, 404))

        transaction.asset_id = args['asset_id']
        transaction.transaction_type = args['transaction_type']
        transaction.transaction_date = datetime.strptime(args['transaction_date'], '%Y-%m-%d').date() if args['transaction_date'] else None

        db.session.commit()
        return make_response(jsonify({'message': 'Transaction updated successfully'}), 201)

    def delete(self, transaction_id):
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
        if not transaction:
            response = make_response(jsonify({'error': 'Transaction not found'}), 404)
            return response

        db.session.delete(transaction)
        db.session.commit()

        return make_response(jsonify({'message': 'Transaction deleted successfully'}, 204))
api.add_resource(TransactionResource, '/transaction/<int:transaction_id>')
class TransactionListResource(Resource):
    def get(self):
        transactions = [transaction.to_dict() for transaction in Transaction.query.all()]
        if not transactions:
            response = make_response(jsonify({'error': 'Transactions not found'}), 404)
            return response

        return make_response(jsonify(transactions), 200)

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('asset_id', type=int, help='Asset ID', required=True)
        parser.add_argument('transaction_type', type=str, help='Transaction type', required=True)
        parser.add_argument('transaction_date', type=str, help='Transaction date')

        args = parser.parse_args()
        new_transaction = Transaction(
            asset_id=args['asset_id'],
            transaction_type=args['transaction_type'],
            transaction_date=datetime.strptime(args['transaction_date'], '%Y-%m-%d').date() if args['transaction_date'] else None
        )

        db.session.add(new_transaction)
        db.session.commit()

        return make_response(jsonify({'message': 'Transaction created successfully'}), 201)
api.add_resource(TransactionListResource, '/transactions')

class MaintenanceListResource(Resource):
    def get(self):
        maintenances = [maintenance.to_dict() for maintenance in Maintenance.query.all()]

        return make_response(jsonify(maintenances),200)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('asset_id', type=int, help='Asset ID', required=True)
        parser.add_argument('date_of_maintenance', help='Date of maintenance')
        parser.add_argument('type', type=str, help='Maintenance type', required=True)
        parser.add_argument('description', type=str, help='Maintenance description')
        parser.add_argument("cost",required=True, help="Cost required")


        args = parser.parse_args()

        new_maintenance = Maintenance(
            asset_id=args['asset_id'],
            date_of_maintenance=datetime.strptime(args['date_of_maintenance'], '%d/%m/%Y').date() if args['date_of_maintenance'] else None,
            type=args['type'],
            description=args['description']
        )
        asset = Asset.query.filter_by(id=args['asset_id']).first()
        asset.status = 'Under Maintenance'

        db.session.add(new_maintenance)
        db.session.commit()

        return make_response(jsonify({'message': 'Maintenance created successfully'}),201)

api.add_resource(MaintenanceListResource, '/maintenances')
class MaintenanceResource(Resource):
    def get(self, maintenance_id):
        maintenance = Maintenance.query.filter_by(maintenance_id=maintenance_id).first()
        if not maintenance:
            response = make_response(jsonify({'error': 'Maintenance not found'}), 404)
            return response

        return make_response(jsonify(maintenance.to_dict()),200)

    def put(self, maintenance_id):
        maintenance = Maintenance.query.filter_by(maintenance_id=maintenance_id).first()

        parser = reqparse.RequestParser()

        parser.add_argument('asset_id', type=int, help='Asset ID', required=True)
        parser.add_argument('date_of_maintenance', type=str, help='Date of maintenance', required=True)
        parser.add_argument('type', type=str, help='Maintenance type', required=True)
        parser.add_argument('description', type=str, help='Maintenance description')
        parser.add_argument("maintainance_status",type=str,help="Maintenance status Needed")
        args = parser.parse_args()
        
        if not maintenance:
            response = make_response(jsonify({'error': 'Maintenance not found'}), 404)
            return response
        
   
        asset = Asset.query.filter_by(id=maintenance.asset_id).first()
        asset.status = 'Write-off'

        maintenance.asset_id = args['asset_id']
        maintenance.date_of_maintenance = datetime.strptime(args['date_of_maintenance'], '%Y-%m-%d').date()
        maintenance.type = args['type']
        maintenance.description = args['description']

        db.session.commit()

        return make_response(jsonify({'message': 'Maintenance updated successfully'}), 201)

    def delete(self, maintenance_id):
        maintenance = Maintenance.query.filter_by(maintenance_id=maintenance_id).first()
        if not maintenance:
            response = make_response(jsonify({'error': 'Maintenance not found'}), 404)
            return response

        

        db.session.delete(maintenance)
        db.session.commit()

        response = make_response(jsonify({'message': 'Maintenance deleted successfully'}), 204)
        return response
api.add_resource(MaintenanceResource, '/maintenance/<int:maintenance_id>')

class RequestsResource(Resource):
    def get(self, request_id):
        request_obj = Requests.query.filter_by(request_id=request_id).first()
        if not request_obj:
            response = make_response(jsonify({'error': 'Request not found'}), 404)
            return response

        return make_response(jsonify(request_obj.to_dict()), 200)

    def put(self, request_id):
        request_obj = Requests.query.filter_by(request_id=request_id).first()

        parser = reqparse.RequestParser()

        parser.add_argument('user_id', type=int, help='User ID', required=True)
        parser.add_argument('asset_name', type=str, help='Asset Name', required=True)
        parser.add_argument('description', type=str, help='Request description')
        parser.add_argument('quantity', type=int, help='Quantity', required=True)
        parser.add_argument('urgency', type=str, help='Urgency', required=True)
        parser.add_argument('status', type=str, help='Request status', required=True)

        args = parser.parse_args()

        if not request_obj:
            response = make_response(jsonify({'error': 'Request not found'}), 404)
            return response

        request_obj.user_id = args['user_id']
        request_obj.asset_name = args['asset_name']
        request_obj.description = args['description']
        request_obj.quantity = args['quantity']
        request_obj.urgency = args['urgency']
        request_obj.status = args['status']

        db.session.commit()

        return make_response(jsonify({'message': 'Request updated successfully'}), 201)

    def delete(self, request_id):
        request_obj = Requests.query.filter_by(request_id=request_id).first()
        if not request_obj:
            response = make_response(jsonify({'error': 'Request not found'}), 404)
            return response

        db.session.delete(request_obj)
        db.session.commit()

        response = make_response(jsonify({'message': 'Request deleted successfully'}), 204)
        return response
api.add_resource(RequestsResource, '/request/<int:request_id>')
class RequestListResource(Resource):
    def get(self):
        requests = Requests.query.order_by(Requests.request_id.desc()).all()
        if not requests:
            return make_response(jsonify({'message': 'Requests not found'}, 404))

        serialized_requests = []

        for a_request in requests:
            serialized_request = a_request.to_dict()
            serialized_request['full_name'] = a_request.user_name
            serialized_requests.append(serialized_request)

        return make_response(jsonify(serialized_requests), 200)
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('user_id', type=int, help='User ID', required=True)
        parser.add_argument('asset_name', type=str, help='Asset Name', required=True)
        parser.add_argument('description', type=str, help='Request description')
        parser.add_argument('quantity', type=int, help='Quantity', required=True)
        parser.add_argument('urgency', type=str, help='Urgency', required=True)
        parser.add_argument('status', type=str, help='Request status', required=True)

        args = parser.parse_args()

        new_request = Requests(
            user_id=args["user_id"],
            asset_name=args['asset_name'],
            description=args['description'],
            quantity=args['quantity'],
            urgency=args['urgency'],
            status=args['status']
        )

        db.session.add(new_request)
        db.session.commit()

        return make_response(jsonify({'message': 'Request created successfully'}), 201)
api.add_resource(RequestListResource, '/requests')
class UserRequestsResource(Resource):
    @cross_origin(supports_credentials=True)
    def get(self, user_id):
        user_requests = Requests.query.filter_by(user_id=user_id).all()
        serialized_requests = [request.to_dict() for request in user_requests]

        return jsonify({'user_requests': serialized_requests}), 200

api.add_resource(UserRequestsResource, '/user_requests/<int:user_id>')

#for handling approval
class ApproveRequestResource(Resource):
    def put(self, request_id):
        request_obj = Requests.query.filter_by(request_id=request_id).first()

        if not request_obj:
            response = make_response(jsonify({'error': 'Request not found'}), 404)
            return response

        # Set status to "Approved" when approving
        request_obj.status = 'Approved'
        db.session.commit()

        return make_response(jsonify({'message': 'Request approved successfully'}), 201)
api.add_resource(ApproveRequestResource, '/request/approve/<int:request_id>')
# for handling decline
class DeclineRequestResource(Resource):
    def put(self, request_id):
        request_obj = Requests.query.filter_by(request_id=request_id).first()

        if not request_obj:
            response = make_response(jsonify({'error': 'Request not found'}), 404)
            return response

        # Set status to "Declined" when declining
        request_obj.status = 'Declined'
        db.session.commit()

        return make_response(jsonify({'message': 'Request declined successfully'}), 201)
api.add_resource(DeclineRequestResource, '/request/decline/<int:request_id>')
class UserProfileResource(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return make_response(jsonify({'error': 'User not found'}), 404)

        return make_response(jsonify(user.to_dict()), 200)

    def put(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return make_response(jsonify({'error': 'User not found'}), 404)

        user.full_name = request.json.get('full_name', user.full_name)
        user.email = request.json.get('email', user.email)
        user.role = request.json.get('role', user.role)
        user.department = request.json.get('department', user.department)

        db.session.commit()

        return make_response(jsonify({'message': 'User profile updated successfully'}), 201)

api.add_resource(UserProfileResource, '/user/profile/<int:user_id>')

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found:The requested endpoint(resource) does not exist",
        404
        )
    return response
if __name__ == "__main__":
    app.run(debug=True,port=5555)