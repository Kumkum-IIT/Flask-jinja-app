from flask import current_app as app
from flask import request, flash
from flask import render_template, redirect, url_for
from flask_login import current_user

from applications.models import *

logged_user=None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method=="GET":
        return render_template("user_login.html")
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        try:
            user_from_db=User.query.get(username)
            if user_from_db:
                password_from_db=user_from_db.password
                if password_from_db==password:
                    global logged_user
                    logged_user=username
                    if user_from_db.roles == "Admin":
                        return redirect(url_for("admin_dashboard"))
                    elif user_from_db.roles == "Influencer":
                        print("test")
                        return redirect(url_for("influencer_dashboard"))
                    elif user_from_db.roles == "Sponser":
                        return redirect(url_for("sponser_dashboard"))
                else:
                    return render_template("user_login.html", message="Password failed")
            else:
                return render_template("user_login.html",message="id failed")
        except:
            return "some error"

@app.route("/admin_dashboard", methods=["GET","POST"])
def admin_dashboard():
    print("---------->>", current_user)
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        return render_template("admin_dashboard.html",campaigns=Campaign.query.all())
    if request.method == "POST":
        campaign_ids = [int(campaign.campaign_id) for campaign in Campaign.query.all()]
        for campaign_id in campaign_ids:
            status_key = f"campaign_status_{campaign_id}"
            visibility_key = f"campaign_visibility_{campaign_id}"
            if status_key in request.form and visibility_key in request.form:
                campaign_status = request.form[status_key]
                campaign_visibility = request.form[visibility_key]
                campaign_to_update = Campaign.query.get(campaign_id)
                if campaign_to_update:
                    campaign_to_update.status = campaign_status
                    campaign_to_update.visibility = campaign_visibility
                    print(f"Updated Campaign ID {campaign_id}: Status = {campaign_status}, Visibility = {campaign_visibility}")
        db.session.commit()
        
    return redirect(url_for("admin_dashboard"))

@app.route("/influencer_dashboard", methods=["GET", "POST"])
def influencer_dashboard():
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        print("user-----",logged_user)
        influencer = Influencer.query.filter_by(name=logged_user).first()
        print("influ----",influencer)
        if not influencer:
            return "Influencer not found", 404
        # return render_template("influencer_dashboard.html",influencer=influencer)
    
        active_campaigns = Campaign.query.filter_by(visibility='Public',status='Active').all()
        print("active_campaigns----",active_campaigns)
        new_requests = AdRequest.query.filter_by(influencer_id=influencer.influencer_id, status='Pending').all()

    return render_template("influencer_dashboard.html", influencer=influencer, active_campaigns=active_campaigns, new_requests=new_requests)

@app.route("/campaign_details/<int:campaign_id>")
def campaign_details(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template("camp_details.html", campaign=campaign)

@app.route("/send_ad_request/<int:campaign_id>", methods=["POST"])
def send_ad_request(campaign_id):
    global logged_user
    if request.method == "POST":
        message = request.form.get("message")
        sponser_camps = Sponser_camp.query.filter_by(campaign_id=campaign_id).all()
        if sponser_camps:
            sponser_ids = [sponser_camp.sponser_id for sponser_camp in sponser_camps]
            # Create ad requests for each sponsor
            campaign = Campaign.query.get_or_404(campaign_id)
            influencer = Influencer.query.filter_by(name=logged_user).first()

            for sponsor in sponser_ids:
                ad_request = AdRequest(
                    ad_name=f"Ad request for {campaign.campaign_name}",
                    campaign_id=campaign.campaign_id,
                    sponser_id=sponsor,
                    influencer_id=influencer.influencer_id,
                    messages=message,
                    requirements="",
                    payment_amount=float(campaign.budget),  # Ensure campaign.budget is cast to float
                    status='Pending'
                )
                db.session.add(ad_request)
            
            db.session.commit()
        
    return redirect(url_for('campaign_details', campaign_id=campaign_id))


@app.route("/accept_request/<int:request_id>", methods=["POST"])
def accept_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    ad_request.status = 'Accepted'
    db.session.commit()
    flash('Request accepted successfully!', 'success')
    return redirect(url_for('influencer_dashboard'))

@app.route("/report_request/<int:request_id>", methods=["POST"])
def report_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    ad_request.status = 'Reported'
    db.session.commit()
    flash('Request reported successfully!', 'warning')
    return redirect(url_for('influencer_dashboard'))


@app.route("/sponser_dashboard", methods=["GET","POST"])
def sponser_dashboard():    
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        return render_template("sponser_dashboard.html",campaigns=Campaign.query.all())

@app.route("/influ_register", methods=["GET", "POST"])
def influ_register():
    if request.method=="GET":
        return render_template("influ_register.html")
    if request.method=="POST":
        name=request.form.get("name")
        password=request.form.get("password")  
        category=request.form.get("category") 
        niche=request.form.get("niche") 
        reach=request.form.get("reach") 
        followers=request.form.get("followers")    
        this_user = Influencer.query.filter_by(name = name).first()
        if this_user:
            return "Influencer already exists!"
        else:
            new_influ = Influencer(name = name, password = password, category = category, niche = niche, reach= reach, followers=followers)
            db.session.add(new_influ)
            new_user = User(username = name, password = password,roles="Influencer")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("/")) 
    return render_template('influ_register.html')

@app.route("/sponser_register", methods=["GET", "POST"])
def sponser_register():
    if request.method=="GET":
        return render_template("sponser_register.html")
    if request.method=="POST":
        company_name=request.form.get("company_name")
        password=request.form.get("password")  
        industry=request.form.get("industry") 
        budget=request.form.get("budget") 
        this_user = Sponser.query.filter_by(company_name = company_name).first()
        if this_user:
            return "Sponser already exists!"
        else:
            new_sponser = Sponser(company_name = company_name, password = password, industry = industry, budget = budget)
            db.session.add(new_sponser)
            new_user = User(username = company_name, password = password,roles="Sponser")
            db.session.add(new_user)
            db.session.commit()
            return redirect('/') 
    return render_template('sponser_register.html')

@app.route("/create_campaign", methods=["GET", "POST"])
def create_campaign():
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        return render_template("create_campaign.html")
    if request.method=="POST":
        # extract the data from request
        campaign_name=request.form.get("campaign_name")
        budget=request.form.get("budget")
        start_date=request.form.get("start_date")
        end_date=request.form.get("end_date")
        description=request.form.get("description")
        visibility=request.form.get("visibility")
        goals=request.form.get("goals")
        status=request.form.get("status")
        # create new campaign in db
        new_campaign=Campaign(campaign_name=campaign_name,description=description,end_date=end_date, start_date=start_date, budget=budget,visibility=visibility,goals=goals,status=status)
        db.session.add(new_campaign)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

@app.route("/delete_campaign", methods=["GET", "POST"])
def delete_campaign():
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        campaigns=Campaign.query.all()
        return render_template("delete_campaign.html", campaigns=campaigns)
    if request.method=="POST":
        campaign_id=request.form.get("campaign_id")
        campaign_to_delete=Campaign.query.get(campaign_id)
        db.session.delete(campaign_to_delete)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

@app.route("/update_campaign", methods=["GET", "POST"])
def update_campaign():
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        campaigns=Campaign.query.all()
        return render_template("update_campaign.html", campaigns=campaigns)
    if request.method=="POST":
        campaign_name=request.form.get("campaign_name")
        campaign_id=request.form.get("campaign_id")
        budget=request.form.get("budget")
        start_date=request.form.get("start_date")
        end_date=request.form.get("end_date")
        description=request.form.get("description")
        visibility=request.form.get("visibility")
        goals=request.form.get("goals")
        status=request.form.get("status")
        
        # update new campaign in db
        campaign_to_update=Campaign.query.get(campaign_id)
        campaign_to_update.campaign_name=campaign_name
        campaign_to_update.description=description
        campaign_to_update.end_date=end_date
        campaign_to_update.start_date=start_date
        campaign_to_update.budget=budget
        campaign_to_update.visibility=visibility
        campaign_to_update.goals=goals
        campaign_to_update.status=status

        db.session.commit()
        return redirect(url_for("admin_dashboard"))

@app.route("/add_sponser", methods=["GET", "POST"])
def add_sponser():
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        return render_template("add_sponser.html")
    if request.method=="POST":
        # extract the data from request
        company_name=request.form.get("company_name")
        budget=request.form.get("budget")
        industry=request.form.get("industry")
        
        # create new sponser in db
        new_sponser=Sponser(company_name=company_name, industry=industry, budget=budget)
        db.session.add(new_sponser)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

@app.route("/delete_sponser", methods=["GET", "POST"])
def delete_sponser():
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        sponsers=Sponser.query.all()
        return render_template("delete_sponser.html", sponsers=sponsers)
    if request.method=="POST":
        sponser_id=request.form.get("sponser_id")
        sponser_to_delete=Sponser.query.get(sponser_id)
        db.session.delete(sponser_to_delete)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

@app.route("/update_sponser", methods=["GET", "POST"])
def update_sponser():
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        sponsers=Sponser.query.all()
        return render_template("update_sponser.html", sponsers=sponsers)
    if request.method=="POST":
        company_name=request.form.get("comapany_name")
        sponser_id=request.form.get("sponser_id")
        budget=request.form.get("budget")
        industry=request.form.get("industry")
        
        # update new sponser in db
        sponser_to_update=Sponser.query.get(sponser_id)
        sponser_to_update.company_name=company_name
        sponser_to_update.industry=industry       
        sponser_to_update.budget=budget        

        db.session.commit()
        return redirect(url_for("admin_dashboard"))

@app.route("/assign_camp_spon", methods=["GET", "POST"])
def assign_camp_spon():
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method == 'GET':
        # Fetch all campaigns and sponsors
        campaigns = Campaign.query.all()
        sponsers = Sponser.query.all()

        # Create a dictionary to store checked campaigns for each sponsor
        checked_campaigns = {}
        for sponser in sponsers:
            # Get the list of checked campaigns for each sponsor
            checked_campaigns[sponser.sponser_id] = set(
                camp.campaign_id for camp in Sponser_camp.query.filter_by(sponser_id=sponser.sponser_id).all()
            )

        return render_template("assign_camp_spon.html", campaigns=campaigns, sponsers=sponsers, checked_campaigns=checked_campaigns)
    if request.method == "POST":
        sponsers = Sponser.query.all()
        for sponser in sponsers:
            # Get all existing Sponser_camp entries for this sponser
            existing_entries = Sponser_camp.query.filter_by(sponser_id=sponser.sponser_id).all()
            
            # Create a set of existing campaign IDs for this sponser
            existing_campaign_ids = set(entry.campaign_id for entry in existing_entries)
            
            # Get the new set of campaign IDs from the form
            new_campaign_ids = set()
            for campaign in Campaign.query.all():
                checkbox_name = f"campaigns_assigned_{sponser.sponser_id}_{campaign.campaign_id}"
                if checkbox_name in request.form:
                    new_campaign_ids.add(campaign.campaign_id)
            
            # Add new entries
            for campaign_id in new_campaign_ids - existing_campaign_ids:
                new_entry = Sponser_camp(campaign_id=campaign_id, sponser_id=sponser.sponser_id)
                db.session.add(new_entry)
            
            # Remove entries that are no longer selected
            for campaign_id in existing_campaign_ids - new_campaign_ids:
                entry_to_remove = Sponser_camp.query.filter_by(
                    sponser_id=sponser.sponser_id, 
                    campaign_id=campaign_id
                ).first()
                if entry_to_remove:
                    db.session.delete(entry_to_remove)
            
            print(f"campaign_ids for {sponser.company_name}: {list(new_campaign_ids)}")
        
        # Commit all changes to the database
        db.session.commit()
        return redirect(url_for("assign_camp_spon"))

# @app.route("/summary", methods=["GET"])
# def summary():
#     global logged_user
#     if not logged_user:
#         return redirect(url_for("user_login"))
#     # return a list of all the json objects of chart data for each venue
#     venues=Venue.query.all()
#     venues_json=[venue.to_json() for venue in venues]
#     return render_template("summary.html", venues=venues, venues_json=venues_json)

# for ad in sponser.sponser_ad:
#             if ad.campaign_id in removed_campaign:
#                 db.session.delete(ad)
#                 db.session.commit()
#         print(sponser, type(sponser), campaign_assigned, type(campaign_assigned))