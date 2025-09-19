from flask import Flask
from flask_restful import Api, Resource, reqparse
from models import db, ApprovedClaim

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
api = Api(app)

# --- Request Parsers ---
claim_parser = reqparse.RequestParser()
claim_parser.add_argument("claimant_name", type=str, required=True)
claim_parser.add_argument("village", type=str, required=True)
claim_parser.add_argument("claim_area", type=float, required=True)
claim_parser.add_argument("gps_coordinates", type=str, required=False)
claim_parser.add_argument("status", type=str, required=False, default="Pending")
claim_parser.add_argument("approval_date", type=str, required=False)

# --- Resources ---
class ClaimListResource(Resource):
    def get(self):
        claims = ApprovedClaim.query.all()
        return [{
            "id": c.id,
            "claimant_name": c.claimant_name,
            "village": c.village,
            "claim_area": c.claim_area,
            "gps_coordinates": c.gps_coordinates,
            "status": c.status,
            "approval_date": c.approval_date
        } for c in claims], 200

    def post(self):
        args = claim_parser.parse_args()
        claim = ApprovedClaim(
            claimant_name=args["claimant_name"],
            village=args["village"],
            claim_area=args["claim_area"],
            gps_coordinates=args.get("gps_coordinates"),
            status=args["status"],
            approval_date=args.get("approval_date")
        )
        db.session.add(claim)
        db.session.commit()
        return {"message": "Claim created", "id": claim.id}, 201

# --- Register API ---
api.add_resource(ClaimListResource, "/api/claims")

# --- Run App ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)