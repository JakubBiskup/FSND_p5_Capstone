import unittest
import json
import os
from models import Game, Event, Member, setup_db
from app import create_app
from flask import Flask

TEST_DB_NAME = 'bgstartntestdb'
TEST_DB_PATH = "postgres://postgres:123@{}/{}".format(
    'localhost:5432', TEST_DB_NAME)
ADMIN_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTZlNDMxNzEwZDZlZTBjOGVkYzY3NWUiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODg3OTg1NjQsImV4cCI6MTU4ODg4NDk2NCwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJkZWxldGU6ZXZlbnRzIiwiZGVsZXRlOmdhbWVzIiwiZGVsZXRlOm1lbWJlcnMiLCJlZGl0OmNsdWIiLCJlZGl0OmdhbWVzIiwiam9pbjpldmVudHMiLCJyZWFkOm1lbWJlci1kZXRhaWxzIl19.hGQl5mNR0mnCRgGAsIO66XXtpO1h9MUDtj0Q2kLSbCoDqMRN_NfS-PGzz7YhqgDwsXnviXOotj-87WM6wdM2m-JqBStfxlHFXeK1UiKLGGearkczltJKNWwftcVnL0FIpVK32i1EJrwnhN4ef_t25CRG1CfWZ9sD83j1FqoZ0_0t5SFvtNlLxiXiJKUVcNgSe9Z2ewg_yivnsebJ8IBSZsizvH6-sj7r6yJ31XeE69swf8dh6m1n491a64g0bPI6earC03FJe80lbj3b1DioodPV29oa5HdZd1IP1iEtAWjp-4aZhN1yoekF_tGWu5Nsw9huh_PrpzDfQqcxQyBLBg"
MEMBER_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTI5Y2UxNWI4YzQ0NzBmMDc5MTc5MGIiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODg3OTg5MDEsImV4cCI6MTU4ODg4NTMwMSwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJqb2luOmV2ZW50cyIsInJlYWQ6bWVtYmVyLWRldGFpbHMiXX0.U56ekIfl510ccAJSZ__he6jwi5ir2pkKHClulis8lVOjgy6RJdog__FgwMua6tR_OHfFiTSeolFy4G9fuahVwLjufv8mm_goaQmIPfmkZ9-ODrrGpzItRqHi94aQOp84tPgow1ZylKkysf6Va0zkLvNistCCfOskJoSdDVMBl5PoL8EbfOYhU8BiHu4bZ3JrcyYXTIVJ_MtbyRuG5Tk8RkarhmQIWdjy7jqB1xKRS70xS4J-2qKc3YSoPhPUNGoUx9_3DS7f5czOeOfllXBaOkH8U-IFYvb-glj__u25JVL1SSG8iicKOiaiWetP2btH3wYu7Mk6GoreTVDNykdWxA"
GUEST_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTYzY2RjMzMyMGMxMjBkNDNlNjM5OTAiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODg3OTg5OTMsImV4cCI6MTU4ODg4NTM5MywiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbXX0.P8L9D8Qb83OmR8wAQ1VNDWBUmq8NGvPswLrgnTsbKDzTntem5wcek9ASgojCVxM8erzhPZnyCc2WdNBfi7ogZM6MXJsheL7Xr8MWRz9g5Xj9Kp_TIqN-F0hdAOakI8TofrDumreMXrDo_8GNbbzMel2a8bdOCGfSKQJAozXLld9lYRfFsQYeZUHw2IiAEnBpa4j1VcPky5hZ12DJ_XO5Zoco3YgPOVRrockVoi67Lp-FfA0XYfsl8EsBHd0Bva4W56XCmNsxZ5jGsqHv90wj9h_rVZbwyFHgVvVGHsfsFEYMPPzoRjwYZeAeLf67phnZEL2nsc-FJM-E_nAemHoCmQ"
GUEST_WITHOUT_MEMBER_OBJECT_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTg3M2YzYzZkZTFiMDBjNjY3ZTFkOTciLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODg3OTkwOTUsImV4cCI6MTU4ODg4NTQ5NSwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJqb2luOmV2ZW50cyIsInJlYWQ6bWVtYmVyLWRldGFpbHMiXX0.QrBiBjBD-2lfRfjEjqCV_3ENk4X98--kwSV4Awv-Wascq66XqRFdmrbgUVKfvI9YM4WJk7N69dMX_6-IXVDx3jkeWwb79aJg48AR9XviaMaqQT0tZRao4oPEChQo8pYq73j_LEaJyy6gr4Q8Uvjy_WuQ1cLX-Eal2H3grSJ2UVKCLIGjeMcUxb1mPPqYnTWG5ahLFY0iPaLPGPqb8o-Q4pvo0QdoO91IwXVNEdVFlPscHUNXHAZMkkqgjpS-V746ehEyEo2nHykRTjywd_P3YxutixcElrGFENl5DHDykpdGGNkOMXMmBVyJIpSjgJVMhMft_5bXhojFInwiWI49ew"
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
