from applications.database import db

class User(db.Model):
    username = db.Column(db.String(30),primary_key=True)
    password = db.Column(db.String(50),nullable=False)
    roles = db.Column(db.String(50),nullable=False)  #admin or sponser or influencer
    approved_by_admin = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Influencer(db.Model):
    influencer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    niche = db.Column(db.String(50), nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Numeric())
    earnings = db.Column(db.Float(10,2))

    # Relationships
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)

    def __repr__(self):
        return f'<Influencer {self.name}>'

    def to_json(self):
        return {
            'influencer_id': self.influencer_id,
            'name': self.name,
            'niche': self.niche,
            'followers': self.followers,
            'rating': float(self.rating) if self.rating is not None else None,
            'earnings': self.earnings
        }

class AdRequest(db.Model):
    ad_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ad_name= db.Column(db.String(50), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    sponser_id = db.Column(db.Integer, db.ForeignKey('sponser.sponser_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    messages = db.Column(db.String(200))
    requirements = db.Column(db.String(200), nullable=False)
    payment_amount = db.Column(db.Float(10,2), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    ad_request_by_sponser = db.Column(db.Boolean, default=False)
    ad_request_by_influencer = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<AdRequest {self.ad_request_id}>'

    def to_json(self):
        return {
            'ad_request_id': self.ad_request_id,
            'ad_name': self.ad_name,
            'campaign_id': self.campaign_id,
            'sponser_id': self.sponser_id,
            'influencer_id': self.influencer_id,
            'messages': self.messages,
            'requirements': self.requirements,
            'payment_amount': self.payment_amount,
            'status': self.status,
            'ad_request_by_sponser': self.ad_request_by_sponser,
            'ad_request_by_influencer': self.ad_request_by_influencer
        }

class Campaign(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=False)
    budget = db.Column(db.Numeric(10,2), nullable=False)
    visibility = db.Column(db.String, default='Private')
    goals = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=False)

    # Relationships
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    sponsors = db.relationship('Sponser', secondary='sponser_camp', backref='campaigns')

    def __repr__(self):
        return f'<Campaign {self.campaign_name}>'

    def to_json(self):
        return {
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign_name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'budget': float(self.budget),
            'visibility': self.visibility,
            'goals': self.goals,
            'status': self.status
        }

class Sponser(db.Model):
    sponser_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Float, nullable=False)

    # Relationships
    ad_requests = db.relationship('AdRequest', backref='sponser', lazy=True)

    def __repr__(self):
        return f'<Sponser {self.company_name}>'

    def to_json(self):
        return {
            'sponser_id': self.sponser_id,
            'company_name': self.company_name,
            'industry': self.industry,
            'budget': self.budget
        }

class Sponser_camp(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    sponser_id = db.Column(db.Integer, db.ForeignKey('sponser.sponser_id'))

    def __repr__(self):
        return f'<Sponser_camp {self.id}>'

