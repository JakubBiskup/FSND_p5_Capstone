import unittest
import json##########
import os
from models import *
from app import create_app
from flask import Flask

#SECRET_KEY=os.urandom(32)
TEST_DB_NAME='testcp6'
TEST_DB_PATH="postgres://postgres:123@{}/{}".format('localhost:5432', TEST_DB_NAME)
ADMIN_JWT="Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTZlNDMxNzEwZDZlZTBjOGVkYzY3NWUiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODc0OTg0MzEsImV4cCI6MTU4NzU4NDgzMSwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJkZWxldGU6ZXZlbnRzIiwiZGVsZXRlOmdhbWVzIiwiZGVsZXRlOm1lbWJlcnMiLCJlZGl0OmNsdWIiLCJlZGl0OmdhbWVzIiwiam9pbjpldmVudHMiLCJyZWFkOm1lbWJlci1kZXRhaWxzIl19.mfke3opO5vah3e88AN0gC1x-5vZJzWx3CFH8574otsDJ4g4Rl0TN8p2XJi4kYIxC7LgjmcI_cWoELsVF8JlrQsUd4_ida7WYzvcJAEBDvw5M7t5f13mh6OwURtu9mZaCHPclUDrat1Zl2p7iuUWm1BXT7MM2qx1LQSfPfe4luJWFm3iqWV3IuHcUr5PNpua5Y-wHRmsrZ0V2ih6C4ixYLzf4Tio3P8TEDdQftoqeZaXCdAysZUy08lphJ4KSbHB7WCdi6d3-v48iyqfO68Sp_zx6CX3E4t8_Dezc39vR8hUMcBzM-O6JTrEgXX52bd1AWy_bVbv0b0KwC_T9DzOucg"	
MEMBER_JWT="Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTI5Y2UxNWI4YzQ0NzBmMDc5MTc5MGIiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODc0OTgwNDQsImV4cCI6MTU4NzUwNTI0NCwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJqb2luOmV2ZW50cyIsInJlYWQ6bWVtYmVyLWRldGFpbHMiXX0.vKU9WFIu_wPD-fPFyAM0uVLl8aDtaYTniB4YUXO5pmNiGVLtP73qOCh4XFFQ095cy-GN-JkgDE-NaF5XhMDFx9hyONg4VSFhk1AhyfiP6HK-xgNbop3gZVb9o858WQaGTNQAp_fKm_b-NTkIxMoaZnPGjl-ggfZ-jkaefhpHQGaVos9PomFeqiCwHe2ufPj9kuq6YK-Z_a0FZ7HVK5WqNqnGJ-QOseFcLVPLjOMSGwdXk4MjuUikzCElDR78xfSFZojM45BgoaefLEELSFCvDgoJi_d9X6COcQj8ut94d0KKR_dRGCdcSEHyZwfmasgQVXPH_f_t0f3fK9rh-O-SWA"	
GUEST_JWT="Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTYzY2RjMzMyMGMxMjBkNDNlNjM5OTAiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODc0OTg2MDQsImV4cCI6MTU4NzU4NTAwNCwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbXX0.k-TCAaXxN1scyFsHtv9Jj5BmgcYiutpOAITPLdqtZddJWzQ4elx6O6wPz6Fv7fnAzeGJMz_mvQjQbfZrSdEAgFMvvowFhqz8bIhLU33XEqB95V08iM-qTEtj46ziE-Kv6uO0jvx_y8_PnMQszAoRP3gHdLmAlAIVzY9bTVUu9zcXD8oJkbHR1yffii2t6G_0s9Df8M1U3pHuTVsxjg1hYunEzNqW61pm18P2AXI7AIBuDP-QxAyQpIT-QFWJE7lF54fKzYCt1GTlAacS7mIfSIOfbw6Y5LubGIHcvtYMedz9a0MjAxEnyuFXZGMNVBr4yU6lr8eWS6nogJWdep8x4w"
DOMAIN='localhost'



class ClubTestCase(unittest.TestCase):

    def setUp(self):

        self.app=create_app(database_path=TEST_DB_PATH)
        self.client=self.app.test_client()
        setup_db(self.app,TEST_DB_PATH)
        #self.app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DB_PATH

    def tearDown(self):
        pass




    def test_get_homepage(self):

        res=self.client.get("/")
        self.assertEqual(res.status_code,200)
    
    def test_get_edit_club_form_without_auth(self):
        res=self.client.get('/home/edit')
        self.assertEqual(res.status_code,401)
    
    def test_get_edit_club_form(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.get('/home/edit')
        self.assertEqual(res.status_code,200)
    
    def test_edit_club(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.post('/home/edit',data={'name':'BG club test name','img_link':'https://avatarfiles.alphacoders.com/103/103167.jpg','h1':'TEST Welcome!','welcoming_text':'this could be much longer, but its just a test!','submit':'Save and apply changes'})
        self.assertEqual(res.status_code,302)
    
    def test_edit_club_without_auth(self):
        res=self.client.post('/home/edit',data={'name':'BG club test name','img_link':'https://avatarfiles.alphacoders.com/103/103167.jpg','h1':'TEST Welcome!','welcoming_text':'this could be much longer, but its just a test!','submit':'Save and apply changes'})
        self.assertEqual(res.status_code,401)
    
class GameTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.app=create_app(database_path=TEST_DB_PATH)
        self.client=self.app.test_client()
        setup_db(self.app,TEST_DB_PATH)
        #self.app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DB_PATH

    def tearDown(self):
        pass


    def test_get_all_games_page(self):
        res=self.client.get('/games/all')
        self.assertEqual(res.status_code,200)
    
    def test_get_create_game_form_without_auth(self):
        res=self.client.get('/games/create')
        self.assertEqual(res.status_code,401)

    def test_get_create_game_form(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res=self.client.get('/games/create')
        self.assertEqual(res.status_code,200)
    
    def test_create_game(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res=self.client.post('/games/create',data={'game':0,'title':'Chess','link':'https://lichess.org','submit':'Save'})
        self.assertEqual(res.status_code,302)
    
    def test_create_game_without_auth(self):
        
        res=self.client.post('/games/create',data={'game':0,'title':'Chess','link':'https://lichess.org','submit':'Save'})
        self.assertEqual(res.status_code,401)
    
    def test_own_game(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res=self.client.patch('/games/4/own')
        self.assertEqual(res.status_code,302)
    
    def test_own_game_without_permission(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res=self.client.patch('/games/4/own')
        self.assertEqual(res.status_code,403)

    def test_unown(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res=self.client.delete('/games/4/unown')
        self.assertEqual(res.status_code,200)

    def test_unown_when_not_logged_in(self):
        res=self.client.delete('/games/4/unown')
        self.assertEqual(res.status_code,401)
    
    def test_get_game_edit_form(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.get('/games/4/edit')
        self.assertEqual(res.status_code,200)
    
    def test_get_game_edit_form_without_permission(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res=self.client.get('/games/4/edit')
        self.assertEqual(res.status_code,403)

    def test_edit_game(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.post('/games/4/edit',data={'title':'test game','link':'https://boardgamegeek.com/boardgame/63268/spot-it','submit':'Save'})
        self.assertEqual(res.status_code,302)
    
    def test_edit_nonexistent_game(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.post('/games/952/edit',data={'title':'test game','link':'https://boardgamegeek.com/boardgame/63268/spot-it','submit':'Save'})
        self.assertEqual(res.status_code,404)
    
    def test_search_game(self):
        res=self.client.post('/games/search',data={'search_term':'a'})
        self.assertEqual(res.status_code,200)

    def test_delete_game(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.delete('/games/28/delete')################################what id should I put here?
        self.assertEqual(res.status_code,302)
    
    def test_delete_nonexistent_game(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.delete('/games/345/delete')
        self.assertEqual(res.status_code,404)










if __name__ == "__main__":
    unittest.main()