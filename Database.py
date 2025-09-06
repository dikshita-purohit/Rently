from bson import ObjectId
from pymongo import MongoClient
import yaml
import random

class Database:
    def __init__(self):
        self.MONGODB = str

        with open("config/mongodb.yml", "r") as file:
            self.MONGODB = yaml.safe_load(file)["MongoDB"]

    def __connect(self):
        Client = MongoClient(self.MONGODB)
        db = Client["Rently"]
        return db

    def register(self, username, email, password, phoneNumber, address):
        db = self.__connect()
        Collection = db["Credentials"]
        while True:
            id = random.randrange(1, 100)
            print("ID:", id,"\n")
            result = self.__checkId(id, email, "Credentials")
            if result == "email":
                return "email"
            elif result:
                Collection.insert_one({"_id":id, "UserName":username, "Email": email, "Password":password, "PhoneNumber": phoneNumber, "Address": address})
                return True
            else:
                return False
            
            
    def __checkId(self,id, email, collectionName):
        db = self.__connect()
        Collection = db[collectionName]
        print(id, email)
        result = Collection.find_one({"Email": email})
        if result:
            print("Email exist")
            return "email"
        else:
            result = Collection.find_one({"_id": id})
            if result:
                return False
            else:
                return True

    def login(self, email, password):
        db = self.__connect()
        Collection = db["Credentials"]
        result = Collection.find_one({"Email":email, "Password": password}, None)
        return result
        
    def getProperties(self):
        try:
            db = self.__connect()
            Collection = db["Seller"]
            result = Collection.find()
            return result
        except:
            return None
    
    def __checkBuildName(self, buildName):
        db = self.__connect()
        collection = db["Seller"]
        result = collection.find_one({"BuildName": buildName})
        if result:
            return False
        else:
           return True

    def SaveSellerData(self, sellerId, buildName, buildAddr, buildDes, buildRooms, buildGarag, buildBaths, buildSqrt, buildPrice, buildType, is_buied, is_rented):
        try:
            if(self.__checkBuildName(buildName) == False):
                return "Exist"
            
            db = self.__connect()
            collection = db["Seller"]
            result = collection.insert_one({"SellerId":sellerId,"BuildName":buildName, "BuildAddr":buildAddr, "BuildDes":buildDes, "BuildPrice":buildPrice, "BuildRooms":buildRooms, "BuildBaths": buildBaths, "BuildGarags":buildGarag, "BuildSqrt":buildSqrt, "BuildType":buildType, "is_buied": is_buied, "is_rentad":is_rented}) 
            
            return result.inserted_id
        except :
            return False
        
    def sellerSignUp(self, sellerUserName, sellerId, sellerEmail, sellerPasswd, sellerPhoneNumber, sellerAddress):
        db = self.__connect()
        collection = db["SellerCredentials"]
        while True:
            id = random.randrange(1, 100)
            print("ID:", id,"\n")
            result = self.__checkId(id, sellerEmail, "SellerCredentials  jtd")
            if result == "email":
                return "email"
            elif result:
                collection.insert_one({"_id":id, "UserName":sellerUserName, "SellerId": sellerId, "Email": sellerEmail, "Password":sellerPasswd, "PhoneNumber": sellerPhoneNumber, "Address": sellerAddress})
                return True
            else:
                return False
            
    def sellerSignIn(self, sellerId, password):
        db = self.__connect()
        collection = db["SellerCredentials"]
        result = collection.find_one({"SellerId":sellerId, "Password": password}, None)
        return result
    
    def getSingleHouseDetails(self, id):
        db = self.__connect()
        collection = db["Seller"]
        result = collection.find_one({"_id":ObjectId(id)}, None)
        return result
    
    def getPropertiesSell(self):
        db = self.__connect()
        collection = db["PropertiesSell"]
        result = collection.find()
        print(result)
        return result
    
    
    def setPropertiesSell(self, data):
        db = self.__connect()
        collection = db["PropertiesSell"]
        result = collection.insert_one(data)
        if(result.inserted_id):
            return True
        else:
            return False
        
    def setPropertiesRent(self, data):
        db = self.__connect()
        collection = db["PropertiesRent"]
        result = collection.insert_one(data)
        if(result.inserted_id):
            return True
        else:
            return False

    
    def getPropertiesRent(self):
        db = self.__connect()
        collection = db["PropertiesRent"]
        result = collection.find()
        print(result)
        return result
    
    def getUserData(self, id):
        db = self.__connect()
        collection = db["Credentials"]
        result = collection.find_one({"_id": id}, None)
        print(result)
        return result
    
    def getSellerDetails(self, id):
        db = self.__connect()
        collection = db["SellerCredentials"]
        result = collection.find_one({"_id": id}, None)
        return result
    
    def updateHouseData(self, filter, new_data):
        db = self.__connect()
        collection = db["Seller"]
        result = collection.update_one(filter, new_data)
        
        if(result.modified_count > 0):
            print("Document updated successfully")
            return "success"
        else:
            print("No document was updated")
            return "failed"
        
    def deleteHome(self, id):
        db = self.__connect()
        collection = db["Seller"]
        print(id)
        result = collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count > 0:
            print("delete success")
            return "success"
        else:
            print("delete failed")
            return "failed"
        
    def updateUserDate(self, filter, new_data):
        db = self.__connect()
        collection = db["Credentials"]
        result = collection.update_one(filter, new_data)
        
        if(result.modified_count > 0):
            print("Document updated successfully")
            return "success"
        else:
            print("No document was updated")
            return "failed"
    
    def updateSellerData(self, filter, new_data):
        db = self.__connect()
        collection = db["SellerCredentials"]
        result = collection.update_one(filter, new_data)
        
        if(result.modified_count > 0):
            print("Document updated successfully")
            return "success"
        else:
            print("No document was updated")
            return "failed"
    def addIntrested(self, user_id, house_id, current_data):
        db = self.__connect()
        collection = db["Intrested"]
        result = collection.insert_one({"userId":user_id, "houseId": house_id, "appliedDate": current_data})
        if result.inserted_id:
            return True
        else:
            return False
    
    def intrestedClicked(self, house_id, user_id):
        db = self.__connect()
        collection = db["Intrested"]
        result = collection.find_one({"userId":user_id,"houseId" : house_id})
        print(result)
        if(result):
            return True
        else:
            return False
    def getIntrestedList(self, house_id):
        db = self.__connect()
        collection = db["Intrested"]
        result = collection.find({"houseId": house_id})
        print(result)
        return result
    
    def approve(self, user_id, house_id, approvedDate):
        db = self.__connect()
        collection = db["Approved"]
        result = collection.insert_one({"userId":user_id, "houseId": house_id, "approvedDate": approvedDate})
        if result.inserted_id:
            return True
        else:
            return False
    def removeHouseApplied(self, house_id, user_id):
        db = self.__connect()
        collection = db["Intrested"]
        print({"userId": user_id, "houseId": house_id})
        result = collection.delete_one({"userId": int(user_id), "houseId": house_id})
        if(result.deleted_count > 0):
            return True
        else:
            return False
        
    def getApprovedData(self, user_id):
        db = self.__connect()
        collection = db["Approved"]
        print({"userId:": str(user_id)})
        result = collection.find({"userId": str(user_id)})
        print("data: ",result)
        return result
    
    def removeApprovedData(self, house_id, user_id):
        db = self.__connect()
        collection = db["Approved"]
        result = collection.delete_one({"userId": str(user_id), "houseId": house_id})
    
    def setPurchasePropertie(self, houseId, userName, phoneNumber, address, email, familyMemberName, familyMemberAddres, familyMemeberPhoneNumber, marital, prevOwnerName, prevOwnerPhoneNumber):
        db = self.__connect()
        collection = db["UploadData"]
        result = collection.insert_one({"HouseId": houseId, "UserName": userName, "PhoneNumber": phoneNumber, "Address": address, "Email":email, "FamilyMemberName":familyMemberName, "FamilyMemberAddres": familyMemberAddres, "FamilyMemeberPhoneNumber": familyMemeberPhoneNumber,"Marital": marital, "PrevOwnerName":prevOwnerName, "PrevOwnerPhoneNumber": prevOwnerPhoneNumber})
        if result.inserted_id:
            return True
        else:
            return False
        
    def getPurchasePropertie(self, id):
        db = self.__connect()
        collection = db["UploadData"]
        result = collection.find_one({"HouseId": id})
        return result 
            
    def updatePropertieData(self, filter, new_data):
        db = self.__connect()
        collection = db["Seller"]
        result = collection.update_one(filter, new_data)
        
        if(result.modified_count > 0):
            print("Document updated successfully")
            return "success"
        else:
            print("No document was updated")
            return "failed"