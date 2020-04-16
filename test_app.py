import unittest
import json##########
import os
from models import *
from app import create_app
from flask import Flask

#SECRET_KEY=os.urandom(32)
TEST_DB_NAME='testcp6'
TEST_DB_PATH="postgres://postgres:123@{}/{}".format('localhost:5432', TEST_DB_NAME)
ADMIN_JWT="Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTZlNDMxNzEwZDZlZTBjOGVkYzY3NWUiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODcwNTk3NzMsImV4cCI6MTU4NzA2Njk3MywiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJkZWxldGU6ZXZlbnRzIiwiZGVsZXRlOmdhbWVzIiwiZGVsZXRlOm1lbWJlcnMiLCJlZGl0OmNsdWIiLCJlZGl0OmdhbWVzIiwiam9pbjpldmVudHMiLCJyZWFkOm1lbWJlci1kZXRhaWxzIl19.HYxAuS-AZ7B0FUCnavhK5ufRn8r2vPoXEANlJtW22_IsauakUESDKnKM7JcJou78TfsreJqnb74AKdsGZ9Iq3hQOMjGjndppwTgxAaU4ELHJSor0_lySbneyT4DPoYsjhIHUA4bDCpdBGC6aM658FX9eOV_gfjzBiBYGdgkxcw6sXqtPOGFiwpxl-Ue98XbC1HUnJHcGvxKeS-pZCpdevIycBoyeVml4SSjgPbCYSaYy6z3aKEwvJjsMoLZr0-e_gYA8ed8GPqKXQrdjCWgQjixmIPk8UbDar7AHelZ1kKZeyAq4QDVoXPsewFclvp0f88pjxvsq-YxvstQRr3WcDw"	
MEMBER_JWT=''
GUEST_JWT=''
DOMAIN='localhost'



class ClubTestCase(unittest.TestCase):

    def setUp(self):

        self.app=create_app()
        self.client=self.app.test_client()
        setup_db(self.app,TEST_DB_PATH)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DB_PATH
        #self.app.config['SECRET_KEY']=SECRET_KEY
    def tearDown(self):
        pass




    def test_get_homepage(self):

        res=self.client.get("/")
        self.assertEqual(res.status_code,200)
    
    def test_get_edit_club_form(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.get('/home/edit')
        self.assertEqual(res.status_code,200)
        









if __name__ == "__main__":
    unittest.main()