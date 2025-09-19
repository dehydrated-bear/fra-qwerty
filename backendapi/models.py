from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ApprovedClaim(db.Model):
    __tablename__ = "approved_claims"

    id = db.Column(db.Integer, primary_key=True)
    claimant_name = db.Column(db.String(120), nullable=False)
    village = db.Column(db.String(120), nullable=False)
    claim_area = db.Column(db.Float, nullable=False)
    gps_coordinates = db.Column(db.String(100), nullable=True)  # e.g. "23.45, 75.23"
    status = db.Column(db.String(50), default="Pending")
    approval_date = db.Column(db.String(50), nullable=True)
