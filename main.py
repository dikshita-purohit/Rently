from bson import ObjectId
from flask import Flask, redirect, url_for, render_template, request, session
from Database import Database
import yaml
import os
import base64
import datetime

app = Flask(__name__)

IMAGE_PATH = None
SECRET_KEY = None
DOC_PATH = None


with open("config/config.yml", "r") as file:
    data = yaml.safe_load(file)
    SECRET_KEY  = data["Secret"]
    print(data["ImagePath"])
    IMAGE_PATH = data["ImagePath"]
    DOC_PATH = data["DocPath"]

app.secret_key = SECRET_KEY

# login function
@app.route("/sign-in", methods = ['POST', 'GET'])
def login(): 
    if request.method == "GET":
        message = session.pop("loginMessage", "")
        return render_template("login-pages/Sign-In.html")
    elif request.method == "POST": 
        Email = request.form.get("email")
        Passwd = request.form.get("passwd")
        if Email and Passwd:
            DatabaseResult = Database().login(Email, Passwd)
            if DatabaseResult: 
                session["id"] = DatabaseResult.get("_id", None)
                session["UserName"] = DatabaseResult.get("Username", None)
                print(session) 
                session["is_seller"] = False
                return redirect(url_for("Home"))
            else:
                return render_template("login-pages/Sign-In.html", error="Enter correct credentials")
        else:
            return render_template("login-pages/Sign-In.html", error="Enter All the field")

# register function
@app.route("/sign-up", methods = ['GET', 'POST'])
def register():
    if request.method == "GET": 
        return render_template("login-pages/Sign-Up.html")
    elif request.method == "POST": 
        user = request.form.get("user")
        email = request.form.get("user-email")
        passwd = request.form.get("passwd")
        phoneNumber = request.form.get("phoneNumber")
        address = request.form.get("address")
        print(user,email,passwd)
        if(user and email and passwd and phoneNumber and address):
            DatabaseResult = Database().register(user, email, passwd, phoneNumber, address) 

            if DatabaseResult == "email":
                print(f"User email {email} alrady exist")
                return render_template("login-pages/Sign-Up.html", error="Email already exist")
            elif DatabaseResult:
                session['loginMessage'] = "Login Successfully"
                
                return redirect(url_for("login"))
            else:
                return render_template("login-pages/Sign-Up.html", error="Failed to sing-up")
        else:
            return render_template("login-pages/Sign-Up.html", error="Enter all the field")

@app.route("/home/house-edit", methods=["GET", "POST"])
def editHome():
    if request.method == "GET":
        house_id = request.args.get('id')
        session["HouseID"] = house_id
        result = Database().getSingleHouseDetails(house_id)
        print(result)
        data = {
            "buildData" : result,
            "error" : session.get("")
        }
        return render_template("home/editHome.html", data = data)
    elif request.method == "POST":
        BName = request.form.get("buildName") 
        BAddr = request.form.get("buildAddr")
        BDes = request.form.get("buildDes")
        BRooms = request.form.get("buildRooms")
        BGar = request.form.get("buildGarag")
        BBaths = request.form.get("buildBaths")
        Bsqrt = request.form.get("buildSqrt")
        BPrice = request.form.get("buildPrice")
        BType = request.form.get("buildType")
        files = request.files.getlist("MultipleFileUpload[]")
        is_buied = False
        is_rented = False

        filter = {"_id": ObjectId(session["HouseID"])}
        new_data = {
            "$set": {
                "BuildName": BName,
                "BuildAddr": BAddr,
                "BuildDes": BDes,
                "BuildPrice": BPrice,  # Update BuildPrice to a new value
                "BuildRooms": BRooms,  # Update BuildRooms to 4
                "BuildBaths": BBaths,  # Leave BuildBaths as is or update if needed
                "BuildGarags": BGar,  # Leave BuildGarags as is or update if needed
                "BuildSqrt": Bsqrt,  # Update BuildSqrt to 2200
                "BuildType": BType,  # Update BuildType to "Rent" if needed
            }
        }
        result = Database().updateHouseData(filter, new_data)

        if(result == "success"):
            print(len(files), "\n\n\n\n")
            if(len(files) > 1):
                path = IMAGE_PATH + "\\" + session["HouseID"]
                os.system(f"del /F /Q {path}")
                print("delete dir")
                os.makedirs(path, exist_ok=True)
                print("form:", request.form)
                print("files:",request.files)

                for index, file in enumerate(files):
                    print(index, file)
                    fileN = f'image_{index + 1}{os.path.splitext(file.filename)[1]}' # Save the file with the new filename 
                    file.save(os.path.join(path, fileN))
            return redirect(url_for("Profile"))
        else:
            return redirect(url_for("Profile"))

            
@app.route("/home/house-delete", methods=["GET"])
def deleteHome():
    house_id = request.args.get("id")
    result = Database().deleteHome(house_id)
    if(result == "success"):
        return redirect(url_for("Profile"))
    else:
        return redirect(url_for("Profile"))
    
# dashboard function
@app.route("/home", methods = ['GET'])
def Home():
    session["HouseID"] = ""
    session["RentHouseID"] = ""

    if(session.get("is_seller") is None):
        session["is_seller"] = False
    data = {
        "User": session.get("id", ""),
        "is_seller": session["is_seller"]
    }
    return render_template("home/index.html", data = data)


@app.route("/home/buy", methods = ['GET'])
def buy():
    session["HouseID"] = ""
    result = list(Database().getProperties())
    print("Data: ", result)
    if(result is not None):
        result = [i for i in result if i.get("is_buied") == False and i.get("BuildType") == "Sell"]

    print(result)

    data = {
        "BuildData": result,
        "is_seller": session.get("is_seller")
    }
    return render_template("home/buy.html", data=data)

@app.route("/home/rent", methods = ['GET'])
def rent():
    session["RentHouseID"]  =  ""
    result = list(Database().getProperties())
    print("Data: ", result)
    if(result is not None):
        result = [i for i in result if i.get("is_rentad") == False and i.get("BuildType") == "Rent"]

    print(result)

    data = {
        "BuildData": result,
        "is_seller": session.get("is_seller")
    }
    return render_template("home/rent.html", data=data)

@app.route("/home/house", methods = ['GET'])
def house():
    if(session.get("id")):
        house_id = request.args.get('id')
        session["HouseID"] = house_id
        print(house_id)
        houseData = Database().getSingleHouseDetails(house_id)
        properties = [i for i in list(Database().getProperties()) if i.get("_id") != ObjectId(house_id) and i.get("BuildType") == "Sell"]
        is_applied = Database().intrestedClicked(house_id, session.get("id"))
        print(is_applied)
        data = {
            "houseData": houseData,
            "properties": properties,
            "is_seller": session["is_seller"],
            "error" : session.get("ApplyError"),
            "is_applied" : is_applied
        }
        session["ApplyError"] = ""
        #print(houseData,"\n", properties)
        return render_template("home/house.html", data = data)
    else:
        return redirect(url_for("login"))

@app.route("/home/rentHome", methods = ['GET'])
def rentHouse():
    house_id = request.args.get('id')
    session["RentHouseID"] = house_id
    print(house_id)
    houseData = Database().getSingleHouseDetails(house_id)
    properties = [i for i in list(Database().getProperties()) if i.get("_id") != ObjectId(house_id) and i.get("BuildType") == "Rent"]
    is_applied = Database().intrestedClicked(house_id, session.get("id"))

    data = {
        "houseData": houseData,
        "properties": properties,
        "is_seller": session["is_seller"],
        "is_applied" : is_applied
    }
    print(houseData,"\n", properties)
    return render_template("home/house.html", data = data)

@app.route("/profile", methods = ['GET'])
def Profile():
    if session["is_seller"]:
        sellerProperties = []
        soldProperties = []
        rentedProperties = []
        propertiesData = Database().getProperties()

        for i in propertiesData:
            if( i.get("SellerId") == session["id"] and i.get("is_buied") == False and i.get("is_rentad") == False):
                sellerProperties.append(i)
            elif i.get("is_rentad") == True and i.get("BuildType") == "Rent":
                rentedProperties.append(i)
            elif i.get("is_buied") == True and i.get("BuildType") == "Sell":
                soldProperties.append(i)
        
        #print([i for i in propertiesData if i.get("SellerId") == session["id"] and i.get("is_buied") == False and i.get("is_rentad") == False])
        #print(session["id"] == propertiesData[0].get("SellerId"), propertiesData[0].get("is_buied") == False, propertiesData[0].get("is_rentad") == False, propertiesData[0], propertiesData[0].get("is_build"))
        #soldProperties = [i for i in propertiesData if i.get("is_buied") == True and i.get("BuildType") == "Sell"]
        #rentedProperties = [i for i in propertiesData if i.get("is_rentad") == True and i.get("BuildType") == "Rent"]
        #sellerProperties = [i for i in propertiesData if i.get("SellerId") == session["id"] and i.get("is_buied") == False and i.get("is_rentad") == False]
        sellerDetails = Database().getSellerDetails(session["id"])

        data = {
            "sold" : soldProperties,
            "rent" : rentedProperties,
            "properties" : sellerProperties,
            "userData" : sellerDetails,
            "is_seller" : session["is_seller"]
        }
        print(data)
        return render_template("/profiles/Profile.html", data = data)
    else:
        sellProperties = [ i for i in Database().getPropertiesSell()]
        rentProperties = [ i for i in Database().getPropertiesRent()]
        approvedData = Database().getApprovedData(session.get('id'))

        propertiesSell = []
        propertiesRent = []
        latestProperties = []
        print("Data: " ,sellProperties, "\n\n", rentProperties)
        if(len(sellProperties) > 0):
            propertiesSell = [ i for i in sellProperties[:-1]]
            sellProperties[-1]["is_approved"] = True
            latestProperties.append(sellProperties[-1])
        if(len(rentProperties) > 0):
            propertiesRent = [ i for i in rentProperties[:-1]]
            rentProperties[-1]["is_approved"] = True
            latestProperties.append(rentProperties[-1])
        if(approvedData):
            print("\nappending")            
            for i in approvedData:
                print(i,"\n")
                result = Database().getSingleHouseDetails(i["houseId"])
                if(result):
                    result["is_approved"] = False
                    latestProperties.append(result)
            #if(len(approvedPropertied) > 0):
            #    latestProperties.append(approvedPropertied)
        userDetails = Database().getUserData(session["id"])
        print(session["id"])
        data = {
            "latest" : latestProperties,
            "Sell" : propertiesSell,
            "Rent" : propertiesRent,
            "userData" : userDetails,
            "is_seller" : session["is_seller"],
            "is_approved": True if approvedData else False
        }

        print("\n\n", data)
        return render_template("/profiles/Profile.html", data = data)
    
@app.route("/profile/edit", methods = ["GET", "POST"])
def editProfile():
    if request.method == "GET":
        if(session.get("is_seller")):
            result = Database().getSellerDetails(session.get("id"))
        else:
            result = Database().getUserData(session.get("id"))
        data = {
            "userData" : result,
            "is_seller" : session.get("is_seller"),
            "error": session.get("profileEditError")
        }
        session["profileEditError"] = None
        return render_template("profiles/editProfile.html", data = data)
    elif request.method == "POST":
        user = request.form.get("user")
        seller_id = request.form.get("sellerId")
        email = request.form.get("email")
        passwd = request.form.get("passwd")
        phoneNumber = request.form.get("phoneNumber")
        address = request.form.get("address")
        print(user,email,passwd)
        if(user and email and passwd and phoneNumber and address):
           
            filter = {"_id": session["id"]}
            if(session.get("is_seller")):
                new_data = {
                    "$set": {
                        "UserName": user,
                        "SellerId": seller_id,
                        "Email": email,
                        "PhoneNumber": phoneNumber,  
                        "Address": address, 
                        "Password": passwd                        
                    }
                }
                print("update seller")
                DatabaseResult = Database().updateSellerData(filter, new_data)
            else:
                new_data = {
                    "$set": {
                        "UserName": user,
                        "Email": email,
                        "PhoneNumber": phoneNumber,  
                        "Address": address, 
                        "Password": passwd                        
                    }
                }
                print("update user")
                DatabaseResult = Database().updateUserDate(filter, new_data)

            if DatabaseResult == "success":                
                return redirect(url_for("Profile"))
            else:
                session["profileEditError"] = "Failed to update"
                return redirect(url_for("editProfile"))       
        else:
            session["profileEditError"] = "Enter all details"
            return redirect(url_for("editProfile"))


@app.route("/home/seller", methods=["GET", "POST"])
def saleFunction():
    if request.method == "GET": 
        return render_template("home/saler.html")
    elif request.method == "POST":
        
        BName = request.form.get("buildName") 
        BAddr = request.form.get("buildAddr")
        BDes = request.form.get("buildDes")
        BRooms = request.form.get("buildRooms")
        BGar = request.form.get("buildGarag")
        BBaths = request.form.get("buildBaths")
        Bsqrt = request.form.get("buildSqrt")
        BPrice = request.form.get("buildPrice")
        BType = request.form.get("buildType")
        files = request.files.getlist("MultipleFileUpload[]")
        is_buied = False
        is_rented = False

        result = Database().SaveSellerData(session["id"],BName, BAddr, BDes, BRooms, BGar, BBaths, Bsqrt, BPrice, BType, is_buied, is_rented)
        if(result == "Exist"):
            return render_template("home/saler.html", error="Building Name aleready exist!")
        elif(result == False):
            return render_template("home/saler.html")
        else:
            path = IMAGE_PATH + "\\" + str(result)
            os.makedirs(path, exist_ok=True)
            print("form:", request.form)
            print("files:",request.files)

            for index, file in enumerate(files):
                print(index, file)
                fileN = f'image_{index + 1}{os.path.splitext(file.filename)[1]}' # Save the file with the new filename 
                file.save(os.path.join(path, fileN))
            return redirect(url_for("Home"))

@app.route("/seller/sign-up", methods=["GET", "POST"])
def sellerSignUp():
    if request.method == "GET":
        return render_template("seller/signUp/sign-up.html")
    elif request.method == "POST":
        sellerUser = request.form.get("user") 
        sellerId = request.form.get("salerId")
        sellerEmail = request.form.get("email")
        sellerPasswd = request.form.get("passwd")
        sellerPhoneNumber = request.form.get("phoneNumber")
        sellerAddress = request.form.get("address")

        if sellerUser and sellerId and sellerEmail and sellerPasswd and sellerPhoneNumber and sellerAddress:
            result = Database().sellerSignUp(sellerUser, sellerId, sellerEmail, sellerPasswd, sellerPhoneNumber, sellerAddress)
            if(result == "email"):
                return render_template("seller/signUp/sign-up.html", error="Email already exist")
            elif result:
                session['loginMessage'] = "Login Successfully"
                return redirect(url_for("Home"))
            else:
                return render_template("seller/signUp/sign-up.html", error="Failed to sign-up")
        else:
            return render_template("seller/signUp/sign-up.html", error="Enter all the field")


@app.route("/seller/sign-in", methods=["GET", "POST"])
def sellerSignIn():
    if request.method == "GET":
        return render_template("seller/signUp/sign-in.html")
    elif request.method == "POST":
        sellerId = request.form.get("sellerId")
        Passwd = request.form.get("passwd")
        if sellerId and Passwd:
            DatabaseResult = Database().sellerSignIn(sellerId, Passwd)
            if DatabaseResult: 
                session["id"] = DatabaseResult.get("_id", None)
                session["UserName"] = DatabaseResult.get("Username", None)
                print(session)
                session["is_seller"] = True
                return redirect(url_for("Home"))
            else:
                return render_template("seller/signUp/sign-in.html", error="Enter correct credentials")
        else:
            return render_template("seller/signUp/sign-in.html", error="Enter All the field")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("Home"))

@app.route("/admin", methods = ['GET'])
def admin():
    return render_template("admin.html")

@app.route("/home/house/intrested", methods = ["GET"])
def intrested():
    house_id = request.args.get('id')
    #houseData = Database().getSingleHouseDetails(house_id)
    user_id = session["id"]
    currentDateTime = datetime.datetime.now()
    print(user_id, currentDateTime)
    if(session["is_seller"]):
        return redirect(url_for("buy"))
    else:
        result = Database().addIntrested(user_id, house_id, currentDateTime)
        if(result):
            return redirect(f"/home/house?id={house_id}")
        else:
            session["ApplyError"] = "Failed to apply"
            return redirect(f"/home/house?id={house_id}")

@app.route("/approved", methods = ["GET"])
def approved():
    user_id =  request.args.get("user_id")
    house_id = request.args.get("house_id")
    approvedDate = datetime.datetime.now()

    result = Database().approve(user_id, house_id, approvedDate)
    if(result):
        print(Database().removeHouseApplied(house_id, user_id))
        return redirect(url_for("Profile"))
    else:
        return redirect(f"/home/house/intrested?id={house_id}")


@app.route("/home/form", methods = ['GET', 'POST'])
def Form():
    if( request.method == "GET"):
        seller_id = request.args.get("id")
        session["houseId"] = request.args.get("houseId")
        return render_template("/home/form.html")
    elif request.method == "POST": 

        userName = request.form["uname"]
        phoneNumber = request.form["pnumber"]
        address = request.form["address"]
        email = request.form["email"]
        parentName =request.form["parname"]
        parentAddress = request.form["paraddress"]
        parentNumber = request.form["parmobnumber"]
        marital=request.form["marital"]
        PreOwnname = request.form["preownname"]
        PreownNumber = request.form["preownnumber"]

        files = request.files.getlist("MultipleFileUpload[]")


        result = Database().setPurchasePropertie(session.get('houseId'), userName, phoneNumber,address,email, parentName, parentAddress, parentNumber,marital,PreOwnname ,PreownNumber)
        if(result):
            Database().removeApprovedData(session.get("houseId"), session.get("id"))
            houseData = Database().getSingleHouseDetails(session.get("houseId"))

            if(houseData["BuildType"] == "Sell"):
                new_data = {"$set": {"is_buied:": True}}
                Database().setPropertiesSell(houseData)
            else:
                new_data = {"$set": {"is_rentad": True}}
                Database().setPropertiesRent(houseData)
            filter = {"_id": ObjectId(session.get("houseId"))}
            
            Database().updatePropertieData(filter, new_data)

            # create dir for doc using doc/id hoseuid 
            path = DOC_PATH + "\\" + str(session.get("houseId"))
            os.makedirs(path, exist_ok=True)
            print("files:",files)

            for index, file in enumerate(files):
                print(index, file)
                fileN = f'doc_{index + 1}{os.path.splitext(file.filename)[1]}' # Save the file with the new filename 
                file.save(os.path.join(path, fileN))          

        return redirect(url_for("Profile"))

@app.route("/home/house-applied", methods = ['GET'])
def Approval():
    house_id = request.args.get("id")
    result = Database().getIntrestedList(house_id)
    userDatas = []
    for i in result:
        result = Database().getUserData(i["userId"])
        result["Applied_date"] = i["appliedDate"]
        result["houseId"] = house_id
        userDatas.append(result)
    data = {
        "userDatas" : userDatas
    }
    return render_template("/home/approve.html", data = data)

@app.route("/home/user-document", methods=["GET"])
def viewUserDocument():
    house_id = request.args.get("id")
    userData = Database().getPurchasePropertie(house_id)
    print(userData)
    data = {
        "userData":userData
    }
    return render_template("home/viewDocument.html", data=data)

if __name__ == "__main__":
    app.run(debug=True, port=8080)

