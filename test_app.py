import unittest
import json##########
import os
from models import *
from app import create_app
from flask import Flask

#SECRET_KEY=os.urandom(32)
TEST_DB_NAME='testcp6'
TEST_DB_PATH="postgres://postgres:123@{}/{}".format('localhost:5432', TEST_DB_NAME)
ADMIN_JWT="Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTZlNDMxNzEwZDZlZTBjOGVkYzY3NWUiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODc3MjQ3NzMsImV4cCI6MTU4NzgxMTE3MywiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJkZWxldGU6ZXZlbnRzIiwiZGVsZXRlOmdhbWVzIiwiZGVsZXRlOm1lbWJlcnMiLCJlZGl0OmNsdWIiLCJlZGl0OmdhbWVzIiwiam9pbjpldmVudHMiLCJyZWFkOm1lbWJlci1kZXRhaWxzIl19.tj_HrZBkhrrNSeeQes05Eyzd7tdrLFWEMRpDcH7wHcbh8N4J5CwV8QiiMgjshcQtDN6JaK724E2WRlwdvDBaWAqS30ZaqBLdobOjrv5UdxVpQl5fhAYywWCOTN77WOtS6wYDxTIz35R_zpnFnOY_rqC6xs8PX227aVBpYJlZh_T6XWe1NhfwUeOww3wwjvFRM884p8Cvyl-07BCOxCQLz7mkfvKwkWyraDXZvy8R4qIVMuGgakmX5q9Zv9XW850wqdnL1_yUHGKZGbuCN9-qy1h61NRfUbjsybMxkuxvyZf2gblCu45AYWPU8LXXN32a8Ij5WqBcyjgvf25Zs6i3VQ"	
MEMBER_JWT="Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTI5Y2UxNWI4YzQ0NzBmMDc5MTc5MGIiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODc3MjQ3MjQsImV4cCI6MTU4NzgxMTEyNCwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJqb2luOmV2ZW50cyIsInJlYWQ6bWVtYmVyLWRldGFpbHMiXX0.bWP4lE_8Us-y00EIv3TjdQIthb6_n3gqGfbvgMdl5gqewCaIXRR5IebyotUpVDviaAM7K2YcgFL-uO1HbW51UEl9vXSVdVNmGNsHQXrqKAg6D5lLedDO79jf4eXY3wjXHS1gBhcHN1Quj3S4E6tvePeJRZUYEtxM0c5fZywe27bGC-ELnK4yslMWyRg8wupzGLat1xKR9apQ5NaJMqUsREaAWTyomUytsEnKonDBTRIjJTj5xJNBVUTKPd9Nyn-ilGj4k4HcGOd5h-B71zeli14o9_-yL83ZBAMqAERcQrbZ51HarTGMvnsn7m5aKpoMZH0HQ_XNR1AP5-puaaPKOQ"	
GUEST_JWT="Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTYzY2RjMzMyMGMxMjBkNDNlNjM5OTAiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODc3MjQ2NTgsImV4cCI6MTU4NzgxMTA1OCwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbXX0.u8ESrFVB49MWokTyrOp-SuXxfHnmHQ_PF_TO2CADCA2SRSj97ZbUFAopEqQdbQGQBggRWhkjCUCEIkomBExMRzxjWVzG-KnOwBI3C5F9JHXgxyyA4odi_T8Hb4vL6Ho94OZdT0hETM-i_S1xN_PpL_oxU_DagPCBKuu-Y1vzXwoPAVPwXRngb0y3jOBMaA_8q5RJ80Wos_GlLXWzjoVTsVVrx23jWPQKTcVZKKcIMqphC4LatEoXZ3OYowG2Vn1nLfJrjGHadVM2h7VroTpD3qD_oACiza3rg8-nU2MGVLNEN_d7TCK1QHE5R-ecpe4Z6wDliIAv1a7sv0fr0J_j8A"
GUEST_WITHOUT_MEMBER_OBJECT_JWT="Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZWEzMmRmZWQyYzA4NzBiZTYxMmJlN2MiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODc3NTI0NDksImV4cCI6MTU4NzgzODg0OSwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbXX0.pVrSTOiOzHo92HBVjiFVKPuWnGlkXn3v2lvCVHaJPpijf0WHf4j9jXFf6kAVGNaTHot7iazhrjnqMfN7ldOhWct67nG5m5mifzPILU0JNHktnvW_zg3Iatr1zfnScLMcM1bM3f1KkwxoAwD0g7NQTfqUso8yYW8xibb_HffMB43ViOJ2rcaU_eyAgSaPx-oTQGxUvy4kb9U2ZjNyzspl5lARRLYN6UQ0aWrJOxICcJaBUvGK3-mpmrdMsEt4JD4RswmCmpcosemA_sa8ubWvYROHe4u3vE2FavUppbPJ3BIVXBdr7hM6wGzAPrj63AKLtjlI0KPnbEnN7JmfVFc4Cw"
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
        res=self.client.post('/games/create',data={'game':0,'title':'test game, delete this','link':'https://lichess.org','submit':'Save'})
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
        game_to_delete_id=Game.query.order_by(Game.id.desc()).first().id
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.delete('/games/'+str(game_to_delete_id)+'/delete')
        self.assertEqual(res.status_code,302)
    
    def test_delete_nonexistent_game(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.delete('/games/345/delete')
        self.assertEqual(res.status_code,404)

class EventTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.app=create_app(database_path=TEST_DB_PATH)
        self.client=self.app.test_client()
        setup_db(self.app,TEST_DB_PATH)
        

    def tearDown(self):
        pass

    def test_get_all_events_page(self):
        res=self.client.get('/events/all')
        self.assertEqual(res.status_code,200)

    def test_get_create_event_form(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res=self.client.get('/events/create')
        self.assertEqual(res.status_code,200)
    
    def test_get_create_event_form_without_permission(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res=self.client.get('/events/create')
        self.assertEqual(res.status_code,403)
    
    def test_create_event(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res=self.client.post('/events/create', data={'name':'test name','description':'test description','time':'2020-12-20 17:45','games':4,'max_players':4,'location':3,'submit':'Create event'})
        self.assertEqual(res.status_code,302)

    def test_create_event_without_auth(self):
        res=self.client.post('/events/create', data={'name':'test2','description':'test description','time':'2020-12-20 17:45','games':4,'max_players':4,'location':3,'submit':'Create event'})
        self.assertEqual(res.status_code,401)
    
    def test_view_one_event(self):
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.get('/events/'+str(newest_event.id))
        self.assertEqual(res.status_code,200)

    def test_get_edit_event_form(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.get('/events/'+str(newest_event.id)+'/edit')
        self.assertEqual(res.status_code,200)

    def test_get_edit_event_form_of_event_hosted_by_another_member(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.get('/events/'+str(newest_event.id)+'/edit')
        self.assertEqual(res.status_code,403)
    
    def test_edit_event(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.post('/events/'+str(newest_event.id)+'/edit',data={'name':'edited name test ','description':'edited test description','time':'2020-12-20 17:45','games':27,'max_players':2,'location':7,'submit':'Edit event'})
        self.assertEqual(res.status_code,302)
    
    def test_edit_event_without_auth(self):
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.post('/events/'+str(newest_event.id)+'/edit',data={'name':'edited name test ','description':'edited test description','time':'2020-12-20 17:45','games':27,'max_players':2,'location':7,'submit':'Edit event'})
        self.assertEqual(res.status_code,401)

    def test_join_event(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.patch('/events/'+str(newest_event.id)+'/join')
        self.assertEqual(res.status_code,200)

    def test_join_event_without_permission(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.patch('/events/'+str(newest_event.id)+'/join')
        self.assertEqual(res.status_code,403)
    
    def test_withdraw(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.patch('/events/'+str(newest_event.id)+'/unjoin')
        self.assertEqual(res.status_code,200)

    def test_withdraw_when_not_logged_in(self):
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.patch('/events/'+str(newest_event.id)+'/unjoin')
        self.assertEqual(res.status_code,401)
    
    def test_search_event(self):
        res=self.client.post('/events/search',data={'search_term':'a'})
        self.assertEqual(res.status_code,200)

    def test_delete_event(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        newest_event=Event.query.order_by(Event.id.desc()).first()
        res=self.client.delete('/events/'+str(newest_event.id)+'/delete')
        self.assertEqual(res.status_code,200)
    
    def test_delete_nonexistent_event(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res=self.client.delete('/events/'+'975'+'/delete')
        self.assertEqual(res.status_code,404)

class MemberTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.app=create_app(database_path=TEST_DB_PATH)
        self.client=self.app.test_client()
        setup_db(self.app,TEST_DB_PATH)
        

    def tearDown(self):
        pass

    def test_get_all_members_page(self):
        res=self.client.get('/members/all')
        self.assertEqual(res.status_code,200)
    
    def test_get_create_member_form(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_WITHOUT_MEMBER_OBJECT_JWT)
        res=self.client.get('/members/create')
        self.assertEqual(res.status_code,200)
    
    def test_get_create_member_form_while_not_logged_in(self):
        res=self.client.get('/members/create')
        self.assertEqual(res.status_code,401)

    
    def test_create_member_object(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_WITHOUT_MEMBER_OBJECT_JWT)
        res=self.client.post('/members/create', data={'username':'test_guest1','img_link':"",'description':'some dummy text here','first_name':'Bartosz','last_name':'Kruk','phone':'123456789','email':'examplemail@gmail.com','country':'','city':'','street':'','house_num':'','appartment_num':'','submit':"Save and apply"})
        self.assertEqual(res.status_code,200)

    def test_create_member_object_when_you_already_have_one(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res=self.client.post('/members/create', data={'username':'test_guest2','img_link':'','description':'some dummy text here','first_name':'Bartosz','last_name':'Kruk','phone':'+48123456789','email':'examplemail@gmail.com','country':'Poland','city':'Katowice','street':'Tarnomariacka','house_num':'12','appartment_num':'3','submit':"Save and apply"})
        self.assertEqual(res.status_code,400)

    def test_get_one_member_page(self):
        newest_member=Member.query.order_by(Member.id.desc()).first()
        res=self.client.get('/members/'+str(newest_member.id))
        self.assertEqual(res.status_code,200)
    
    def test_get_nonexistent_member_page(self):
        res=self.client.get('/members/1156')
        self.assertEqual(res.status_code,404)
    
    def test_get_detailed_member_page(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_member=Member.query.order_by(Member.id.desc()).first()
        res=self.client.get('/members/'+str(newest_member.id)+'/detailed')
        self.assertEqual(res.status_code,200)
    
    def test_get_detailed_member_page_without_auth(self):
        newest_member=Member.query.order_by(Member.id.desc()).first()
        res=self.client.get('/members/'+str(newest_member.id)+'/detailed')
        self.assertEqual(res.status_code,401)
    
    def test_search_member(self):
        res=self.client.post('/members/search',data={'search_term':'a'})
        self.assertEqual(res.status_code,200)

    def test_get_member_edit_form(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res=self.client.get('/members/me/edit')
        self.assertEqual(res.status_code,200)

    def test_get_member_edit_form_not_logged_in(self):
        res=self.client.get('/members/me/edit')
        self.assertEqual(res.status_code,401)

    def test_edit_member(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res=self.client.post('/members/me/edit',data={'username':'EDITEDtest_guest_EDITED','img_link':'','description':'some dummy text here','first_name':'Bartosz','last_name':'Kruk','phone':'+48123456789','email':'examplemail@gmail.com','country':'Poland','city':'Katowice','street':'Tarnomariacka','house_num':'12','appartment_num':'3','submit':"Save and apply"})
        self.assertEqual(res.status_code,302)
    
    def test_edit_member_not_logged_in(self):
        res=self.client.post('/members/me/edit',data={'username':'EDITEDtest_guest_EDITED','img_link':'','description':'some dummy text here','first_name':'Bartosz','last_name':'Kruk','phone':'+48123456789','email':'examplemail@gmail.com','country':'Poland','city':'Katowice','street':'Tarnomariacka','house_num':'12','appartment_num':'3','submit':"Save and apply"})
        self.assertEqual(res.status_code,401)

    def test_delete_member(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        newest_member=Member.query.order_by(Member.id.desc()).first()
        res=self.client.delete('/members/'+str(newest_member.id)+'/delete')
        self.assertEqual(res.status_code,302)
 
    def test_delete_nonexistent_member(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)#############################
        res=self.client.delete('/members/9554/delete')
        self.assertEqual(res.status_code,302)









if __name__ == "__main__":
    unittest.main()