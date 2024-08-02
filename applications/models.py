from applications.database import db

class User(db.Model):
    username = db.Column(db.String(30),primary_key=True)
    password = db.Column(db.String(50),nullable=False)
    roles = db.Column(db.String(50),nullable=False)  #admin or general
    approved_by_admin = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Influencer(db.Model):
    influencer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(100), nullable=True)
    niche = db.Column(db.String(50), nullable=False)
    reach = db.Column(db.Float(10,2), nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Numeric(5,2))
    earnings = db.Column(db.Float(10,2))

    # Relationships
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)
    campaigns = db.relationship('Campaign', secondary='influencer_campaign', backref='influencers')

    def __repr__(self):
        return f'<Influencer {self.name}>'

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

class Sponser_camp(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    sponser_id = db.Column(db.Integer, db.ForeignKey('sponser.sponser_id'))

    def __repr__(self):
        return f'<Sponser_camp {self.id}>'

class InfluencerCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))

    def __repr__(self):
        return f'<InfluencerCampaign {self.id}>'