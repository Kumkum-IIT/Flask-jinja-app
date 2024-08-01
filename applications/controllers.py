from flask import current_app as app
from flask import request
from flask import render_template, redirect, url_for
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
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    if request.method=="GET":
        return render_template("admin_dashboard.html",campaigns=Campaign.query.all())
    if request.method=="POST":
        campaign_status=request.form.getlist("campaign_status")
        campaign_visibility=request.form.getlist("campaign_visibility")
        campaign_id=request.form.getlist("campaign_id")
        for i in range(len(campaign_id)):
            campaign_to_update=Campaign.query.get(campaign_id[i])
            print(campaign_to_update)
            campaign_to_update.status=campaign_status
            print(campaign_to_update.status)
            campaign_to_update.visibility=campaign_visibility
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

@app.route("/influencer_dashboard", methods=["GET","POST"])
def influencer_dashboard():    
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))

    campaigns=Campaign.query.all()
    sponsers=Sponser.query.all()

    return render_template("influencer_dashboard.html",campaigns=campaigns, sponsers=sponsers)

@app.route("/sponser_dashboard", methods=["GET","POST"])
def sponser_dashboard():    
    return render_template("sponser_dashboard.html")

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
        comapany_name=request.form.get("comapany_name")
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
    if request.method=="GET":
        return render_template("assign_camp_spon.html",campaigns=Campaign.query.all(), sponsers=Sponser.query.all())
    if request.method=="POST":
        sponsers=Sponser.query.all()
        for sponser in sponsers:
            campaign_ids=request.form.getlist(f"campaigns_assigned{sponser.sponser_id}")
            print(campaign_ids)
            campaign_assigned=[Campaign.query.get(campaign_id) for campaign_id in campaign_ids]
            print(campaign_assigned)
            already_assigned=sponser.sponser_campaign
            print(already_assigned)
            removed_campaign=[campaign.campaign_id for campaign in already_assigned if campaign not in campaign_assigned]
            
            sponser.sponser_campaign=campaign_assigned
            db.session.commit()
        return redirect(url_for("admin_dashboard"))

@app.route("/summary", methods=["GET"])
def summary():
    global logged_user
    if not logged_user:
        return redirect(url_for("user_login"))
    # return a list of all the json objects of chart data for each venue
    venues=Venue.query.all()
    venues_json=[venue.to_json() for venue in venues]
    return render_template("summary.html", venues=venues, venues_json=venues_json)

# for ad in sponser.sponser_ad:
#             if ad.campaign_id in removed_campaign:
#                 db.session.delete(ad)
#                 db.session.commit()
#         print(sponser, type(sponser), campaign_assigned, type(campaign_assigned))