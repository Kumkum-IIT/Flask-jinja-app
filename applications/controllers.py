from flask import current_app as app
from flask import request, flash
from flask import jsonify
from flask import current_app as app, request, render_template, redirect, url_for, make_response
from flask_jwt_extended import create_access_token, set_access_cookies, jwt_required, get_jwt_identity, unset_jwt_cookies
from applications.models import *
from datetime import timedelta

logged_user=None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method == "GET":
        return render_template("user_login.html")
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        try:
            user_from_db = User.query.filter_by(username=username).first()
            if user_from_db.roles == "Admin" and user_from_db.approved_by_admin == True:
                if user_from_db.password == password:
                    access_token = create_access_token(
                        identity={"username": username, "roles": user_from_db.roles},
                        expires_delta=timedelta(hours=1)
                    )
                    response = make_response(redirect(url_for("admin_dashboard")))
                    set_access_cookies(response, access_token)
                    return response
            elif user_from_db.roles == "Influencer" and user_from_db.approved_by_admin == True:
                if user_from_db.password == password:
                    access_token = create_access_token(
                        identity={"username": username, "roles": user_from_db.roles},
                        expires_delta=timedelta(hours=1)
                    )
                    response = make_response(redirect(url_for("influencer_dashboard")))
                    set_access_cookies(response, access_token)
                    return response
            elif user_from_db.roles == "Sponser" and user_from_db.approved_by_admin == True:
                if user_from_db.password == password:
                    access_token = create_access_token(
                        identity={"username": username, "roles": user_from_db.roles},
                        expires_delta=timedelta(hours=1)
                    )
                    response = make_response(redirect(url_for("sponser_dashboard")))
                    set_access_cookies(response, access_token)
                    return response
            else:
                return render_template("user_login.html", message="Invalid username or password")
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template("user_login.html", message="An unexpected error occurred. Please try again later."), 500

@app.route("/admin_dashboard", methods=["GET", "POST"])
@jwt_required()
def admin_dashboard():
    current_user = get_jwt_identity()
    if current_user["roles"] != "Admin":
        return jsonify({"message": "Access forbidden: Admins only"}), 403

    if request.method == "GET":
        return render_template("admin_dashboard.html", campaigns=Campaign.query.all())

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
        db.session.commit()
    
    return render_template("admin_dashboard.html", campaigns=Campaign.query.all())

@app.route("/influencer_dashboard", methods=["GET", "POST"])
@jwt_required()
def influencer_dashboard():
    current_user = get_jwt_identity()
    if request.method=="GET":
        influencer = Influencer.query.filter_by(name=current_user["username"]).first()
        print("influ----",influencer)
        if not influencer:
            return "Influencer not found", 404
        # return render_template("influencer_dashboard.html",influencer=influencer)
    
        active_campaigns = Campaign.query.filter_by(visibility='Public',status='Active').all()
        print("active_campaigns----",active_campaigns)
        new_requests = AdRequest.query.filter_by(influencer_id=influencer.influencer_id, status='Pending',ad_request_by_sponser=True).all()

    return render_template("influencer_dashboard.html", influencer=influencer, active_campaigns=active_campaigns, new_requests=new_requests)

@app.route("/campaign_details/<int:campaign_id>")
@jwt_required()
def campaign_details(campaign_id):
    current_user = get_jwt_identity()
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template("camp_details.html", campaign=campaign)

@app.route("/send_ad_request/<int:campaign_id>", methods=["POST"])
@jwt_required()
def send_ad_request(campaign_id):
    current_user = get_jwt_identity()
    if request.method == "POST":
        message = request.form.get("message")
        sponser_camps = Sponser_camp.query.filter_by(campaign_id=campaign_id).all()
        if sponser_camps:
            sponser_ids = [sponser_camp.sponser_id for sponser_camp in sponser_camps]
            # Create ad requests for each sponsor
            campaign = Campaign.query.get_or_404(campaign_id)
            influencer = Influencer.query.filter_by(name=current_user["username"]).first()

            for sponsor in sponser_ids:
                ad_request = AdRequest(
                    ad_name=f"Ad request for {campaign.campaign_name}",
                    campaign_id=campaign.campaign_id,
                    sponser_id=sponsor,
                    influencer_id=influencer.influencer_id,
                    messages=message,
                    requirements="",
                    payment_amount=float(campaign.budget),  # Ensure campaign.budget is cast to float
                    status='Pending',
                    ad_request_by_influencer=True
                )
                db.session.add(ad_request)
            
                db.session.commit()
        
    return redirect(url_for('influencer_dashboard', campaign_id=campaign_id))


@app.route("/accept_request/<int:request_id>", methods=["POST"])
@jwt_required()
def accept_request(request_id):
    current_user = get_jwt_identity()
    ad_request = AdRequest.query.get_or_404(request_id)
    ad_request.status = 'Accepted'
    db.session.commit()
    flash('Request accepted successfully!', 'success')
    return redirect(url_for('influencer_dashboard'))

@app.route("/report_request/<int:request_id>", methods=["POST"])
@jwt_required()
def report_request(request_id):
    current_user = get_jwt_identity()
    ad_request = AdRequest.query.get_or_404(request_id)
    ad_request.status = 'Reported'
    db.session.commit()
    flash('Request reported successfully!', 'warning')
    return redirect(url_for('influencer_dashboard'))


@app.route("/sponser_dashboard", methods=["GET", "POST"])
@jwt_required()
def sponser_dashboard():
    current_user = get_jwt_identity()
    print("---curr---",current_user)
    sponsor = Sponser.query.filter_by(company_name=current_user['username']).first()
    if not sponsor:
        return "Sponsor not found", 404

    campaigns = Campaign.query.join(Sponser_camp, Campaign.campaign_id == Sponser_camp.campaign_id)\
                              .filter(Sponser_camp.sponser_id == sponsor.sponser_id).all()

    return render_template("sponser_dashboard.html", sponsor=sponsor, campaigns=campaigns)

@app.route("/influ_register", methods=["GET", "POST"])
def influ_register():
    if request.method=="GET":
        return render_template("influ_register.html")
    if request.method=="POST":
        name=request.form.get("name")
        password=request.form.get("password") 
        niche=request.form.get("niche") 
        followers=request.form.get("followers") 
        ratings=request.form.get("ratings")
        earnings=request.form.get("earnings")

        this_user = Influencer.query.filter_by(name = name).first()
        if this_user:
            return "Influencer already exists!"
        else:
            new_influ = Influencer(name = name, password = password, niche = niche, followers=followers,rating=ratings,earnings=earnings)
            db.session.add(new_influ)
            new_user = User(username = name, password = password,roles="Influencer")
            flash("Registered successfully")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("home")) 
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
            new_user = User(username = company_name, password = password,roles="Sponser", approved_by_admin=False)
            flash("Registered successfully")
            db.session.add(new_user)
            db.session.commit()
            return redirect('/') 
    return render_template('sponser_register.html')

@app.route("/create_campaign", methods=["GET", "POST"])
@jwt_required()
def create_campaign():
    current_user = get_jwt_identity()
    
    if current_user["roles"] == "Sponser" :
        if request.method == "GET":
            return render_template("create_campaign.html")
        
        if request.method == "POST":
            # Extract the data from the request
            campaign_name = request.form.get("campaign_name")
            budget = request.form.get("budget")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            description = request.form.get("description")
            visibility = request.form.get("visibility")
            goals = request.form.get("goals")
            status = request.form.get("status")
            
            existing_campaign = Campaign.query.filter_by(campaign_name=campaign_name).first()
            if existing_campaign:
                return render_template("create_campaign.html", message="This campaign already exists")
            else:
                new_campaign = Campaign(
                    campaign_name=campaign_name,
                    description=description,
                    end_date=end_date,
                    start_date=start_date,
                    budget=budget,
                    visibility=visibility,
                    goals=goals,
                    status=status
                )
                db.session.add(new_campaign)
                db.session.commit()
                return redirect(url_for("sponser_dashboard"))
    
    # If the user is not authorized to create a campaign
    return "Unauthorized", 403

@app.route("/delete_campaign", methods=["GET", "POST"])
@jwt_required()
def delete_campaign():
    current_user = get_jwt_identity()
    if current_user["roles"] == "Sponser":
        if request.method=="GET":
            campaigns=Campaign.query.all()
            return render_template("delete_campaign.html", campaigns=campaigns)
        if request.method=="POST":
            campaign_id=request.form.get("campaign_id")
            campaign_to_delete=Campaign.query.get(campaign_id)
            db.session.delete(campaign_to_delete)
            db.session.commit()
            return redirect(url_for("delete_campaign"))
    return "Unauthorized", 403

@app.route("/update_campaign", methods=["GET", "POST"])
@jwt_required()
def update_campaign():
    current_user = get_jwt_identity()
    if current_user["roles"] == "Sponser":
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
            return redirect(url_for("update_campaign"))

    return "Unauthorized", 403

@app.route("/add_sponser", methods=["GET", "POST"])
@jwt_required()
def add_sponser():
    current_user = get_jwt_identity()
    if current_user["roles"] == "Admin":
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
@jwt_required()
def delete_sponser():
    current_user = get_jwt_identity()
    if current_user["roles"] == "Admin":
        if request.method=="GET":
            sponsers=Sponser.query.all()
            return render_template("delete_sponser.html", sponsers=sponsers)
        if request.method=="POST":
            sponser_id=request.form.get("sponser_id")
            sponser_to_delete=Sponser.query.get(sponser_id)
            db.session.delete(sponser_to_delete)
            db.session.commit()
            return redirect(url_for("delete_sponser"))

@app.route("/update_sponser", methods=["GET", "POST"])
@jwt_required()
def update_sponser():
    current_user = get_jwt_identity()
    if current_user["roles"] == "Admin":
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
            return redirect(url_for("update_sponser"))

@app.route("/assign_camp_spon", methods=["GET", "POST"])
@jwt_required()
def assign_camp_spon():
    current_user = get_jwt_identity()
    if current_user["roles"] != "Admin":
        return jsonify({"message": "Access forbidden: Admins only"}), 403
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

@app.route('/search_influ/<int:campaign_id>')
@jwt_required()
def search_influ(campaign_id):
    current_user = get_jwt_identity()
    campaign = Campaign.query.get_or_404(campaign_id)
    influencers = Influencer.query.filter(Influencer.niche == campaign.goals).all()
    return render_template('search_influ.html', campaign=campaign, influencers=influencers)

@app.route("/influencer/<int:influencer_id>/<int:campaign_id>", methods=["GET"])
@jwt_required()
def view_influ_profile(influencer_id,campaign_id):
    current_user = get_jwt_identity()
    try:
        # Fetch the influencer details from the database
        influencer = Influencer.query.get_or_404(influencer_id)
        campaign = Campaign.query.get_or_404(campaign_id)
        return render_template("view_influ_profile.html", influencer=influencer, campaign=campaign)
    except Exception as e:
        return e  # Redirect to a default page if there's an error
    
@app.route('/send_ad_request_influ/<int:influencer_id>/<int:campaign_id>', methods=['GET', 'POST'])
@jwt_required()
def send_ad_request_influ(influencer_id, campaign_id):
    current_user = get_jwt_identity()
    
    if request.method == 'POST':
        ad_name = request.form.get('ad_name')
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')
        messages = request.form.get('messages')
        sponser_id=Sponser.query.filter_by(company_name=current_user['username']).first().sponser_id

        
        # Assuming you have an AdRequest model and a relationship set up
        ad_request = AdRequest(
            ad_name=ad_name,
            campaign_id=campaign_id,
            requirements=requirements,
            payment_amount=payment_amount,
            messages=messages,
            influencer_id=influencer_id,
            sponser_id=sponser_id,  # Adjust according to your setup
            ad_request_by_sponser=True
        )
        
        db.session.add(ad_request)
        db.session.commit()
        
        # Redirect to a confirmation page or back to the profile
        return redirect(url_for('sponser_dashboard', influencer_id=influencer_id,campaign_id=campaign_id))

    if request.method == 'GET':
        influencer = Influencer.query.get_or_404(influencer_id)
        return render_template('send_ad_request_influ.html', influencer_id=influencer_id, campaign_id=campaign_id, influencer=influencer)


@app.route('/ad_requests')
@jwt_required()
def ad_requests():
    current_user = get_jwt_identity()
    
    sponsor = Sponser.query.filter_by(company_name=current_user['username']).first()
    print(sponsor)
    if not sponsor:
        return redirect(url_for('user_login'))  # Redirect if not a sponsor
    
    ad_requests = AdRequest.query.filter_by(sponser_id=sponsor.sponser_id, ad_request_by_influencer=True).all()
    print(ad_requests)
    return render_template('ad_requests.html', ad_requests=ad_requests, sponsor=sponsor)

@app.route('/accept_ad_request/<int:ad_request_id>')
@jwt_required()
def accept_ad_request(ad_request_id):
    current_user = get_jwt_identity()
    
    sponsor = Sponser.query.filter_by(company_name=current_user['username']).first()

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.sponser_id != sponsor.sponser_id:
        return redirect(url_for('ad_requests'))  # Redirect if not the owner of the request
    
    ad_request.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('ad_requests'))

@app.route('/reject_ad_request/<int:ad_request_id>')
@jwt_required()
def reject_ad_request(ad_request_id):
    current_user = get_jwt_identity()    
    sponsor = Sponser.query.filter_by(company_name=current_user['username']).first()

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.sponser_id != sponsor.sponser_id:
        return redirect(url_for('ad_requests'))  # Redirect if not the owner of the request
    
    ad_request.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('ad_requests'))

@app.route("/approve_sponsors", methods=["GET"])
@jwt_required()
def approve_sponsors():
    current_user = get_jwt_identity()
    unapproved_users = User.query.filter_by(approved_by_admin=False).all()
    return render_template('approve_sponsors.html', unapproved_users=unapproved_users)

@app.route("/approve_user/<username>", methods=["POST"])
@jwt_required()
def approve_user(username):
    current_user = get_jwt_identity()
    user = User.query.get(username)
    if user:
        user.approved_by_admin = True
        db.session.commit()
    return redirect(url_for('approve_sponsors'))

@app.route("/reject_user/<username>", methods=["POST"])
@jwt_required()
def reject_user(username):
    current_user = get_jwt_identity()
    user = User.query.get(username)
    sponsor = Sponser.query.filter_by(company_name=username).first()
    if user:
        db.session.delete(user)
        db.session.delete(sponsor)
        db.session.commit()
    return redirect(url_for('approve_sponsors'))

@app.route("/logout", methods=["GET"])
def logout():
    response = make_response(redirect(url_for("home")))
    unset_jwt_cookies(response)
    return response


@app.route("/summary")
@jwt_required()
def summary():
    # Fetch data
    campaigns = Campaign.query.all()
    sponser_camps = Sponser_camp.query.all()
    ad_requests = AdRequest.query.all()
    
    # Calculate statistics
    campaign_sponsor_counts = {}
    for sponser_camp in sponser_camps:
        campaign_id = sponser_camp.campaign_id
        if campaign_id not in campaign_sponsor_counts:
            campaign_sponsor_counts[campaign_id] = 0
        campaign_sponsor_counts[campaign_id] += 1

    campaigns_data = []
    for campaign in campaigns:
        campaigns_data.append({
            'campaign_name': campaign.campaign_name,
            'sponsor_count': campaign_sponsor_counts.get(campaign.campaign_id, 0)
        })

    total_campaigns = len(campaigns)
    total_sponsors = len(set(s.sponser_id for s in sponser_camps))
    total_active_users = len(Influencer.query.all()) + len(Sponser.query.all())  # Assuming all are active
    public_campaigns = len([c for c in campaigns if c.visibility == 'public'])
    private_campaigns = len([c for c in campaigns if c.visibility == 'private'])
    total_ad_requests = len(ad_requests)
    pending_ad_requests = len([r for r in ad_requests if r.status == 'Pending'])
    approved_ad_requests = len([r for r in ad_requests if r.status == 'Approved'])
    rejected_ad_requests = len([r for r in ad_requests if r.status == 'Rejected'])
    
    # Note: Set flagged counts to 0 if not applicable
    flagged_sponsors = 0
    flagged_influencers = 0

    return render_template(
        "summary.html",
        campaigns_json=campaigns_data,
        total_campaigns=total_campaigns,
        total_sponsors=total_sponsors,
        total_active_users=total_active_users,
        public_campaigns=public_campaigns,
        private_campaigns=private_campaigns,
        total_ad_requests=total_ad_requests,
        pending_ad_requests=pending_ad_requests,
        approved_ad_requests=approved_ad_requests,
        rejected_ad_requests=rejected_ad_requests,
        flagged_sponsors=flagged_sponsors,
        flagged_influencers=flagged_influencers
    )



@app.route("/update_influ_profile", methods=["GET", "POST"])
@jwt_required()
def update_influ_profile():
    current_user = get_jwt_identity()
    print("curr----------",current_user["username"])
    # Fetch the influencer from the database
    influencer = Influencer.query.filter_by(name=current_user["username"]).first()

    if request.method == "GET":
        return render_template("update_influ_profile.html", influencer=influencer)

    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404

    if request.method == "POST":
        # Get data from the form
        name = request.form.get("name")
        niche = request.form.get("niche")
        followers = request.form.get("followers")
        rating = request.form.get("rating")
        earnings = request.form.get("earnings")

        # Update influencer details
        influencer.name = name if name else influencer.name
        influencer.niche = niche if niche else influencer.niche
        influencer.followers = int(followers) if followers else influencer.followers
        influencer.rating = float(rating) if rating else influencer.rating
        influencer.earnings = float(earnings) if earnings else influencer.earnings

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('influencer_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
    
    return render_template("update_influ_profile.html", influencer=influencer)


@app.route("/stats/<int:influencer_id>")
@jwt_required()
def stats(influencer_id):
    print(f"Requested influencer_id: {influencer_id}")  # Debugging line

    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return "Influencer not found", 404

    # Get all ad requests for the given influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id).all()

    # Get all sponsor IDs associated with this influencer
    sponsor_ids = {ad.sponser_id for ad in ad_requests}

    # Fetch ad requests for these sponsors
    ad_requests = AdRequest.query.filter(AdRequest.sponser_id.in_(sponsor_ids)).all()

    # Get all campaigns for these sponsors
    campaign_ids = {ad.campaign_id for ad in ad_requests}
    campaigns = Campaign.query.filter(Campaign.campaign_id.in_(campaign_ids)).all()

    # Count requests by campaign visibility
    public_requests = sum(1 for ad in ad_requests if Campaign.query.get(ad.campaign_id).visibility == 'Public')
    private_requests = sum(1 for ad in ad_requests if Campaign.query.get(ad.campaign_id).visibility == 'Private')

    # Count campaigns by visibility (global counts)
    public_campaigns_count = Campaign.query.filter_by(visibility='Public').count()
    private_campaigns_count = Campaign.query.filter_by(visibility='Private').count()

    # Prepare data for chart
    chart_data = {
        'labels': ['Public Campaigns', 'Private Campaigns'],
        'data': [public_requests, private_requests]
    }

    # Fetch influencer details
    influencer_name = influencer.name if influencer else "Unknown"

    return render_template(
        "influencer_stats.html",
        chart_data=chart_data,
        sponsor_name=influencer_name,
        public_campaigns_count=public_campaigns_count,
        private_campaigns_count=private_campaigns_count
    )

@app.route("/sponser_summary/<int:sponser_id>")
@jwt_required()
def sponser_summary(sponser_id):
    # Fetch sponser
    sponser = Sponser.query.get(sponser_id)
    if not sponser:
        return "Sponser not found", 404

    # Fetch campaigns associated with the sponser
    campaign_ids = [sc.campaign_id for sc in Sponser_camp.query.filter_by(sponser_id=sponser_id).all()]
    campaigns = Campaign.query.filter(Campaign.campaign_id.in_(campaign_ids)).all()

    # Count campaigns by status
    flagged_count = sum(1 for campaign in campaigns if campaign.status == 'Flagged')
    active_count = sum(1 for campaign in campaigns if campaign.status == 'Active')
    pending_count = sum(1 for campaign in campaigns if campaign.status == 'Pending')

    # Prepare data for chart
    influencer_data = {}
    for campaign in campaigns:
        ad_requests = AdRequest.query.filter_by(campaign_id=campaign.campaign_id, sponser_id=sponser_id).all()
        influencers = {Influencer.query.get(ad.influencer_id).name for ad in ad_requests}
        influencer_data[campaign.campaign_name] = list(influencers)

    chart_data = {
        'campaigns': list(influencer_data.keys()),
        'influencers': [', '.join(influencers) for influencers in influencer_data.values()]
    }

    return render_template(
        "sponser_summary.html",
        flagged_count=flagged_count,
        active_count=active_count,
        pending_count=pending_count,
        chart_data=chart_data,
        sponser_name=sponser.company_name
    )


@app.route("/edit_adrequest/<int:ad_request_id>", methods=["GET", "POST"])
@jwt_required()
def edit_adrequest(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    if request.method == "POST":
        ad_request.ad_name = request.form.get('ad_name')
        ad_request.campaign_id = request.form.get('campaign_id')
        ad_request.sponser_id = request.form.get('sponser_id')
        ad_request.influencer_id = request.form.get('influencer_id')
        ad_request.messages = request.form.get('messages')
        ad_request.requirements = request.form.get('requirements')
        ad_request.payment_amount = request.form.get('payment_amount')
        ad_request.status = request.form.get('status')
        ad_request.ad_request_by_sponser = request.form.get('ad_request_by_sponser') == 'on'
        ad_request.ad_request_by_influencer = request.form.get('ad_request_by_influencer') == 'on'

        try:
            db.session.commit()
            flash('Ad request updated successfully!', 'success')
            return redirect(url_for('sponser_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating ad request: {str(e)}', 'danger')

    return render_template('edit_adrequest.html', ad_request=ad_request)

@app.route('/delete_adrequest/<int:ad_request_id>', methods=['GET','POST'])
@jwt_required()
def delete_adrequest(ad_request_id):
    current_user = get_jwt_identity()
    if current_user["roles"] == "Sponser":
        # Fetch the ad request from the database
        print("in delete----------",ad_request_id)
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        print("in delete----------",ad_request_id)
        
        # Delete the ad request
        try:
            db.session.delete(ad_request)
            db.session.commit()
            flash('Ad request deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while deleting the ad request: {str(e)}', 'error')
        
        # Redirect back to the ad requests list
        return redirect(url_for('sponser_dashboard'))  # Adjust this to the appropriate route
