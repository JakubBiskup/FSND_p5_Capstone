import unittest
import json
import os
from models import Game, Event, Member, setup_db
from app import create_app
from flask import Flask

TEST_DB_NAME = 'bgstartntestdb'
TEST_DB_PATH = "postgres://postgres:123@{}/{}".format(
    'localhost:5432', TEST_DB_NAME)
ADMIN_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTZlNDMxNzEwZDZlZTBjOGVkYzY3NWUiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODg4MzgwNjEsImV4cCI6MTU4ODkyNDQ2MSwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJkZWxldGU6ZXZlbnRzIiwiZGVsZXRlOmdhbWVzIiwiZGVsZXRlOm1lbWJlcnMiLCJlZGl0OmNsdWIiLCJlZGl0OmdhbWVzIiwiam9pbjpldmVudHMiLCJyZWFkOm1lbWJlci1kZXRhaWxzIl19.xnU6G2A4bgtzgrTmDeatL_VEPagSX7YYgPlEqOceCy_fofADNDi52w5wXCEJJwwRgs9eEAfDdultuPtgb4B006T5NaKCizYbig5MMPF2Szk7YMHL5k9AI7VxoOOFYOAsYJd_FZSqKkRBI9r3Lhrl-MLRylBqXSG6SBFwhekmiTHKDmc25kuH_H6YaIAsA0SBDgh_nmG5BQABU1lqIFyF5Wff1Nrk6CT3SPWWvHE6iWGIYh8awvu8G6GlFwcnBJ76U5V9aW8hVkBa5EtXMH2vt4mlxD8I6q3gwPPYlim6hcIsRb9huCCJhf8CxNH-U8aWVMTmUUJZFc9wHpD9Q41d8w"
MEMBER_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTI5Y2UxNWI4YzQ0NzBmMDc5MTc5MGIiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODg4MzgxMzIsImV4cCI6MTU4ODkyNDUzMiwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJqb2luOmV2ZW50cyIsInJlYWQ6bWVtYmVyLWRldGFpbHMiXX0.ahmQ32dLK6Qk8iL-S8GKKc0uY3NepD2QlapUv76er1-huLQMAqhDOwG7H-Cv7HDN-vd5na7sOnlvkXwtzjKISTLmGOWDyZ93InrKF6_gglgfxs-JXhyOfa8SJswe7EoT7sHR8E-qmr9BkGeKDvwB86gCzavAcqE5K8xIG3ekbrXEokuC_R2nw7zewYWUutVEXIIzCMhsK2YrZfsN5HboU3yMbkA-NDhDYpnb3AEtd1eqOSouln5t3vXVxzfwppWt13nUOFn8ogn-bT0MgMwkmbpoFAlMA4vEpnLt4L4tlpZCNDuDdVhgUlGKYFdXdaUhBeOuKdPfX-V1lQnt9G6sfQ"
GUEST_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTYzY2RjMzMyMGMxMjBkNDNlNjM5OTAiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODg4MzgyMzgsImV4cCI6MTU4ODkyNDYzOCwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbXX0.yS7YXmj0vt5acuM5FrgFhYyFJtLJZv1eglvlz4_nh2DCU6KwhOsNKrX5kC5eqD24ksCLIQYYlPuYh3VKIY0V-nWRms83MpjDU3lt0YePRu1hA_Ry7pOj2ClmUO5JRhzwjqAiAxtdbAM0ddQ31zr5O2pFqdg80vPjOR9g4Tib_Dv2jEOlqeREsqiS4Qusnxwh-2-dFcDrVJ-UkQtRZQFz4hCXYsC7C7Y5rohRR6mk415D3jghMFXXXlaDjXuIlQp1bPO2hWxmZwiqmg_I7fpjJ7WHjULEDrclqh4WhAfB5Gca91Y797QfDWJkNXiVUT4nsGuuM36DkbUUi3WUvDL_gQ"
GUEST_WITHOUT_MEMBER_OBJECT_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTg3M2YzYzZkZTFiMDBjNjY3ZTFkOTciLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODg4MzgzMjMsImV4cCI6MTU4ODkyNDcyMywiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJqb2luOmV2ZW50cyIsInJlYWQ6bWVtYmVyLWRldGFpbHMiXX0.egH41iNIr2lAERiObjWvR11b3gr6znS3lmdNc8gVfqaF973qsIX_wgLffBk9knby_k8_54YVauhwsqILcDOtzJMhmctHDg8iGjukitxPIs9uldD5TZF7UFGdEgo-ApsQvEKH2h6_PuyO1Qg-GWqxU6uUsoNWasoHCR2vt_4qX1H22ppiSb5Ctr74cgkzZ5MVcdXkMrrlLkp8jDm2tXQuiJU3n5o0klmd1ESj6IdxwxW51qGaCxt_fe9SdbuTQjGm34hfq-grmHDZ_B8ix7f9GzzdIvfVTbV33kucsW0lfT6wFxVR5wREggfGkLFttcLWNI1Djwzw8vK7qKb39Q7gOA"
DOMAIN = 'localhost'


class LoginTestCase(unittest.TestCase):

    def setUp(self):

        self.app = create_app(test_config=None, database_path=TEST_DB_PATH)
        self.client = self.app.test_client()
        setup_db(self.app, TEST_DB_PATH)

    def tearDown(self):
        pass

    def test_get_login_page(self):
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)

    def test_save_cookie_on_login(self):
        res = self.client.post('/login', data={'after_hash': 'access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTYzY2RjMzMyMGMxMjBkNDNlNjM5OTAiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODgwMDExODEsImV4cCI6MTU4ODA4NzU4MSwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbXX0.PSlgiDlue84cBw3_ok_5W5DwEODWf4heJDg9lDhtztj5729LQ77NiDB3hgVJEyg9hc-aNxNFy3jTSVSa3INpl9g0qGdG6NWF8fCiJahOzvURmv-LVjDuEyx9IqN_vqY9tcPJvBQKlNySrGZvXM1MktuNLo9781iHZ1OgkE0LIRpXxyqpON7dBUbEN_Xzd4xlAWGnUZlJ6v2Q7qJH_fp_soO-k82Rqx2L_2VFg9UoIK3nSGP0fUUbH8-UY7qFe8Etb7HxCbz4zlDVG9ZMy0KnR0FHHjY3XO3TPTdQJGNgoB3hrIe_jfuKALsChgEpgUsiM9kr0x24dO3JTUKt55igBw&expires_in=86400&token_type=Bearer'})
        self.assertEqual(res.status_code, 302)


class ClubTestCase(unittest.TestCase):

    def setUp(self):

        self.app = create_app(test_config=None, database_path=TEST_DB_PATH)
        self.client = self.app.test_client()
        setup_db(self.app, TEST_DB_PATH)

    def tearDown(self):
        pass

    def test_get_homepage(self):

        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

    def test_get_edit_club_form_without_auth(self):
        res = self.client.get('/home/edit')
        self.assertEqual(res.status_code, 401)

    def test_get_edit_club_form(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res = self.client.get('/home/edit')
        self.assertEqual(res.status_code, 200)

    def test_edit_club(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res = self.client.post(
            '/home/edit',
            data={
                'name': 'BG club test name',
                'img_link': 'https://avatarfiles.alpha' +
                'coders.com/103/103167.jpg',
                'h1': 'TEST Welcome!',
                'welcoming_text': 'this could be much longer' +
                ', but its just a test!',
                'submit': 'Save and apply changes'})
        self.assertEqual(res.status_code, 302)

    def test_edit_club_without_auth(self):
        res = self.client.post(
            '/home/edit',
            data={
                'name': 'BG club test name',
                'img_link': 'https://avatarfiles.alpha' +
                'coders.com/103/103167.jpg',
                'h1': 'TEST Welcome!',
                'welcoming_text': 'this could be much longer' +
                ', but its just a test!',
                'submit': 'Save and apply changes'})
        self.assertEqual(res.status_code, 401)


class GameTestCase(unittest.TestCase):

    def setUp(self):

        self.app = create_app(test_config=None, database_path=TEST_DB_PATH)
        self.client = self.app.test_client()
        setup_db(self.app, TEST_DB_PATH)

    def tearDown(self):
        pass

    def test_get_all_games_page(self):
        res = self.client.get('/games/all')
        self.assertEqual(res.status_code, 200)

    def test_get_create_game_form_without_auth(self):
        res = self.client.get('/games/create')
        self.assertEqual(res.status_code, 401)

    def test_get_create_game_form(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res = self.client.get('/games/create')
        self.assertEqual(res.status_code, 200)

    def test_create_game(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res = self.client.post(
            '/games/create',
            data={
                'game': 0,
                'title': 'test game, delete this',
                'link': 'https://lichess.org',
                'submit': 'Save'})
        self.assertEqual(res.status_code, 302)

    def test_create_game_without_auth(self):

        res = self.client.post(
            '/games/create',
            data={
                'game': 0,
                'title': 'Chess',
                'link': 'https://lichess.org',
                'submit': 'Save'})
        self.assertEqual(res.status_code, 401)

    def test_own_game(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res = self.client.patch('/games/4/own')
        self.assertEqual(res.status_code, 302)

    def test_own_game_without_permission(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res = self.client.patch('/games/4/own')
        self.assertEqual(res.status_code, 403)

    def test_unown(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res = self.client.delete('/games/4/unown')
        self.assertEqual(res.status_code, 200)

    def test_unown_when_not_logged_in(self):
        res = self.client.delete('/games/4/unown')
        self.assertEqual(res.status_code, 401)

    def test_get_game_edit_form(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res = self.client.get('/games/4/edit')
        self.assertEqual(res.status_code, 200)

    def test_get_game_edit_form_without_permission(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res = self.client.get('/games/4/edit')
        self.assertEqual(res.status_code, 403)

    def test_edit_game(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res = self.client.post(
            '/games/4/edit',
            data={
                'title': 'test game',
                'link': 'https://boardgamegeek.com/boardgame/63268/spot-it',
                'submit': 'Save'})
        self.assertEqual(res.status_code, 302)

    def test_edit_nonexistent_game(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res = self.client.post(
            '/games/952/edit',
            data={
                'title': 'test game',
                'link': 'https://boardgamegeek.com/boardgame/63268/spot-it',
                'submit': 'Save'})
        self.assertEqual(res.status_code, 404)

    def test_search_game(self):
        res = self.client.post('/games/search', data={'search_term': 'a'})
        self.assertEqual(res.status_code, 200)

    def test_delete_game(self):
        game_to_delete_id = Game.query.order_by(Game.id.desc()).first().id
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res = self.client.delete(
            '/games/' +
            str(game_to_delete_id) +
            '/delete')
        self.assertEqual(res.status_code, 302)

    def test_delete_nonexistent_game(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res = self.client.delete('/games/345/delete')
        self.assertEqual(res.status_code, 404)


class EventTestCase(unittest.TestCase):

    def setUp(self):

        self.app = create_app(test_config=None, database_path=TEST_DB_PATH)
        self.client = self.app.test_client()
        setup_db(self.app, TEST_DB_PATH)

    def tearDown(self):
        pass

    def test_get_all_events_page(self):
        res = self.client.get('/events/all')
        self.assertEqual(res.status_code, 200)

    def test_get_create_event_form(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res = self.client.get('/events/create')
        self.assertEqual(res.status_code, 200)

    def test_get_create_event_form_without_permission(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res = self.client.get('/events/create')
        self.assertEqual(res.status_code, 403)

    def test_create_event(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        res = self.client.post(
            '/events/create',
            data={
                'name': 'test name',
                'description': 'test description',
                'time': '2020-12-20 17:45',
                'games': 4,
                'max_players': 4,
                'location': 3,
                'submit': 'Create event'})
        self.assertEqual(res.status_code, 302)

    def test_create_event_without_auth(self):
        res = self.client.post(
            '/events/create',
            data={
                'name': 'test2',
                'description': 'test description',
                'time': '2020-12-20 17:45',
                'games': 4,
                'max_players': 4,
                'location': 3,
                'submit': 'Create event'})
        self.assertEqual(res.status_code, 401)

    def test_view_one_event(self):
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.get('/events/' + str(newest_event.id))
        self.assertEqual(res.status_code, 200)

    def test_get_edit_event_form(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.get('/events/' + str(newest_event.id) + '/edit')
        self.assertEqual(res.status_code, 200)

    def test_get_edit_event_form_of_event_hosted_by_another_member(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.get('/events/' + str(newest_event.id) + '/edit')
        self.assertEqual(res.status_code, 403)

    def test_edit_event(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.post(
            '/events/' + str(
                newest_event.id) + '/edit',
            data={
                'name': 'edited name test ',
                'description': 'edited test description',
                'time': '2020-12-20 17:45',
                'games': 27,
                'max_players': 2,
                'location': 7,
                'submit': 'Edit event'})
        self.assertEqual(res.status_code, 302)

    def test_edit_event_without_auth(self):
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.post(
            '/events/' + str(
                newest_event.id) + '/edit',
            data={
                'name': 'edited name test ',
                'description': 'edited test description',
                'time': '2020-12-20 17:45',
                'games': 27,
                'max_players': 2,
                'location': 7,
                'submit': 'Edit event'})
        self.assertEqual(res.status_code, 401)

    def test_join_event(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.patch('/events/' + str(newest_event.id) + '/join')
        self.assertEqual(res.status_code, 200)

    def test_join_event_without_permission(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.patch('/events/' + str(newest_event.id) + '/join')
        self.assertEqual(res.status_code, 403)

    def test_withdraw(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.patch('/events/' + str(newest_event.id) + '/unjoin')
        self.assertEqual(res.status_code, 200)

    def test_withdraw_when_not_logged_in(self):
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.patch('/events/' + str(newest_event.id) + '/unjoin')
        self.assertEqual(res.status_code, 401)

    def test_search_event(self):
        res = self.client.post('/events/search', data={'search_term': 'a'})
        self.assertEqual(res.status_code, 200)

    def test_delete_event(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.delete('/events/' + str(newest_event.id) + '/delete')
        self.assertEqual(res.status_code, 200)

    def test_delete_nonexistent_event(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res = self.client.delete('/events/' + '975' + '/delete')
        self.assertEqual(res.status_code, 404)


class MemberTestCase(unittest.TestCase):

    def setUp(self):

        self.app = create_app(test_config=None, database_path=TEST_DB_PATH)
        self.client = self.app.test_client()
        setup_db(self.app, TEST_DB_PATH)

    def tearDown(self):
        pass

    def test_get_all_members_page(self):
        res = self.client.get('/members/all')
        self.assertEqual(res.status_code, 200)

    def test_get_create_member_form(self):
        self.client.set_cookie(
            DOMAIN, 'token', GUEST_WITHOUT_MEMBER_OBJECT_JWT)
        res = self.client.get('/members/create')
        self.assertEqual(res.status_code, 200)

    def test_get_create_member_form_while_not_logged_in(self):
        res = self.client.get('/members/create')
        self.assertEqual(res.status_code, 401)

    def test_create_member_object(self):
        self.client.set_cookie(
            DOMAIN, 'token', GUEST_WITHOUT_MEMBER_OBJECT_JWT)
        res = self.client.post(
            '/members/create',
            data={
                'username': 'test_guest1',
                'img_link': "",
                'description': 'some dummy text here',
                'first_name': 'Bartosz',
                'last_name': 'Kruk',
                'phone': '123456789',
                'email': 'examplemail@gmail.com',
                'country': '',
                'city': '',
                'street': '',
                'house_num': '',
                'appartment_num': '',
                'submit': "Save and apply"})
        self.assertEqual(res.status_code, 200)

    def test_create_member_object_when_you_already_have_one(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res = self.client.post(
            '/members/create',
            data={
                'username': 'test_guest2',
                'img_link': '',
                'description': 'some dummy text here',
                'first_name': 'Bartosz',
                'last_name': 'Kruk',
                'phone': '+48123456789',
                'email': 'examplemail@gmail.com',
                'country': 'Poland',
                'city': 'Katowice',
                'street': 'Tarnomariacka',
                'house_num': '12',
                'appartment_num': '3',
                'submit': "Save and apply"})
        self.assertEqual(res.status_code, 400)

    def test_get_one_member_page(self):
        newest_member = Member.query.order_by(Member.id.desc()).first()
        res = self.client.get('/members/' + str(newest_member.id))
        self.assertEqual(res.status_code, 200)

    def test_get_nonexistent_member_page(self):
        res = self.client.get('/members/1156')
        self.assertEqual(res.status_code, 404)

    def test_get_detailed_member_page(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_member = Member.query.order_by(Member.id.desc()).first()
        res = self.client.get(
            '/members/' + str(newest_member.id) + '/detailed')
        self.assertEqual(res.status_code, 200)

    def test_get_detailed_member_page_without_auth(self):
        newest_member = Member.query.order_by(Member.id.desc()).first()
        res = self.client.get(
            '/members/' + str(newest_member.id) + '/detailed')
        self.assertEqual(res.status_code, 401)

    def test_search_member(self):
        res = self.client.post('/members/search', data={'search_term': 'a'})
        self.assertEqual(res.status_code, 200)

    def test_get_member_edit_form(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res = self.client.get('/members/me/edit')
        self.assertEqual(res.status_code, 200)

    def test_get_member_edit_form_not_logged_in(self):
        res = self.client.get('/members/me/edit')
        self.assertEqual(res.status_code, 401)

    def test_edit_member(self):
        self.client.set_cookie(DOMAIN, 'token', GUEST_JWT)
        res = self.client.post(
            '/members/me/edit',
            data={
                'username': 'EDITEDtest_guest_EDITED',
                'img_link': '',
                'description': 'some dummy text here',
                'first_name': 'Bartosz',
                'last_name': 'Kruk',
                'phone': '+48123456789',
                'email': 'examplemail@gmail.com',
                'country': 'Poland',
                'city': 'Katowice',
                'street': 'Tarnomariacka',
                'house_num': '12',
                'appartment_num': '3',
                'submit': "Save and apply"})
        self.assertEqual(res.status_code, 302)

    def test_edit_member_not_logged_in(self):
        res = self.client.post(
            '/members/me/edit',
            data={
                'username': 'EDITEDtest_guest_EDITED',
                'img_link': '',
                'description': 'some dummy text here',
                'first_name': 'Bartosz',
                'last_name': 'Kruk',
                'phone': '+48123456789',
                'email': 'examplemail@gmail.com',
                'country': 'Poland',
                'city': 'Katowice',
                'street': 'Tarnomariacka',
                'house_num': '12',
                'appartment_num': '3',
                'submit': "Save and apply"})
        self.assertEqual(res.status_code, 401)

    def test_delete_member(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        newest_member = Member.query.order_by(Member.id.desc()).first()
        res = self.client.delete(
            '/members/' + str(newest_member.id) + '/delete')
        self.assertEqual(res.status_code, 302)

    def test_delete_nonexistent_member(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        res = self.client.delete('/members/9554/delete')
        self.assertEqual(res.status_code, 302)


if __name__ == "__main__":
    unittest.main()
