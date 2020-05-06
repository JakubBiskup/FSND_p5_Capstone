import unittest
import json
import os
from models import Game, Event, Member, setup_db
from app import create_app
from flask import Flask

TEST_DB_NAME = 'testcp5'
TEST_DB_PATH = "postgres://postgres:123@{}/{}".format(
    'localhost:5432', TEST_DB_NAME)
ADMIN_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTZlNDMxNzEwZDZlZTBjOGVkYzY3NWUiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODgxNzExMTcsImV4cCI6MTU4ODI1NzUxNywiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJkZWxldGU6ZXZlbnRzIiwiZGVsZXRlOmdhbWVzIiwiZGVsZXRlOm1lbWJlcnMiLCJlZGl0OmNsdWIiLCJlZGl0OmdhbWVzIiwiam9pbjpldmVudHMiLCJyZWFkOm1lbWJlci1kZXRhaWxzIl19.hPMFwtUIi1BgQrzUiATBRzMidP3MaNWWW_3zXKyIkqwJD2_f1wkYQMPKE2FZeAx05Vri6U_Rd_wEygE_dyvPcDOsaKSynCrCACT58sKTEobSOCSqu6Sp7zNHf2IftXtsf4jjDycUcsNXn6IHMPMoZXB09VfrxmHe1KqtD6UcyS62X6D6Yqdrkc-fwv3Rd7yN3_6A_AQnEkh0fwBMjKPLmYf_g5Olcx09mxXJLzwZPYz9lWqklcsnabdf6RkohhRABpzLPru7KjiRn8uf2_wsGP7AGxtM2y5_r91BvUQA20FQpr0E6WYIhhBDlhg0HIPSCKKCwCNffHgWXxDNgVs6zA"
MEMBER_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTI5Y2UxNWI4YzQ0NzBmMDc5MTc5MGIiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODgxNzEwMzgsImV4cCI6MTU4ODI1NzQzOCwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDpnYW1lcyIsImNyZWF0ZTpldmVudHMiLCJqb2luOmV2ZW50cyIsInJlYWQ6bWVtYmVyLWRldGFpbHMiXX0.Lz6q1uOPtkc5U_2k_RGMKK3piMJ4JDRehI82d5wnG8R4eYPmIVvbiZzHzAe_zoDn5LFQwTntCuov1q0QfA7YsLqIjJgt9MzOpawBVWntJYbI11-Ei23zuRW334wLwLs23z9mGhqBO4-HaARVIyIt3bRsUFRKJ2UL8xoJECEbI_K-I074hl-z3xFTyR1jDdEA-Ku5A4c7ZGjliwhOhA2eVerbDtv_ZucZpGYRdUrGGccWkKvXAg8Dj00eW7xtSJO9bf5qUa5AqXKDv5BOPFKqqhv9JbmcSCe4DqI1LDEZXeA7ReshHBmLUmGPe8yMTlZn8Qvo-8noWob55NJwQKAGZA"
GUEST_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTYzY2RjMzMyMGMxMjBkNDNlNjM5OTAiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODgxNzA4NDYsImV4cCI6MTU4ODI1NzI0NiwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbXX0.RL1mzRfRT6VNyVTW8XrRikJMCqHXrsIgB6ZenpvYgmzBqkuszAHGNXK8HnChu_mQECDdxW92hN3u3AB3XTQQgVpi1bc9QjByx6nAmFLTgFIX05ICNdRHU3vzJJ_acQQZBLt0XQwXEAc57wGGSh2Ss6qRCqEY7E0cW74EUnD_VZEV6XUaAJSngBnpnBe0SpyZ1SdCk2OkWuB4Ry2g5fyYCkcJfDwwF3pObo8kz0_ZMduTwmdIhqV9Rn6-w8N2q67mNfcdSpNAwawmBRdc3CWQKLbGmcYVXdYpucUhIsYleVbde6qYk7PEn9WdvLSHQ9E_QSDssgxXr-CZxQP3cQpgGg"
GUEST_WITHOUT_MEMBER_OBJECT_JWT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5FSkdNVUZETmtSQ09EYzFPVGM0T0VWR01VWXlSRVUzT0RCRU1FVTFNRGhGUVROQ00wUXdNUSJ9.eyJpc3MiOiJodHRwczovL2ZzbmR0ZXN0LmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZWE5OTI0NjY0ODliMTBjMTZhZjlmYjkiLCJhdWQiOiJCaXNob3BHYW1pbmciLCJpYXQiOjE1ODgxNzEzMzksImV4cCI6MTU4ODI1NzczOSwiYXpwIjoiRjF4aWN1Tlo4RVAyOVBsRlIxcnpnSWhEY2hRMkl0WE8iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbXX0.0wp0HXHuaY15LL8SWWTgjDoIojzgNfvoBPtU7U_LsRnQNs16AmZiF7x8qCSWnFvVY1qEnKz3gdz2e4xN6n3T_e3F_gD_BB_7ZMHAGRqicQp06OtSrW0Cv7WO0d_dBwrY2cytVwT-aPkO4F5b0O4-hWGgRjkJQCHiAVVi4EP9sltp7IM0qR10R3aGlNk3i3ewGUtPuOcStstdTRD_mSkxXPCyyYLM7GjEIM9v5Ef7j_s4yOdNvnfcaAEvuGgPL3YZgYzqlChtPGNxGe375TrWPGoL-OTzf1wnJw0P7vE0nFr-4Bxf_r-LnuzB3OO6z5hLpGJ3elyBUjVH8ZWAcY450Q"
DOMAIN = 'localhost'


class LoginTestCase(unittest.TestCase):

    def setUp(self):

        self.app = create_app(test_config=None,database_path=TEST_DB_PATH)
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

        self.app = create_app(test_config=None,database_path=TEST_DB_PATH)
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

        self.app = create_app(test_config=None,database_path=TEST_DB_PATH)
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

        self.app = create_app(test_config=None,database_path=TEST_DB_PATH)
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
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.get('/events/' + str(newest_event.id) + '/edit')
        self.assertEqual(res.status_code, 200)

    def test_get_edit_event_form_of_event_hosted_by_another_member(self):
        self.client.set_cookie(DOMAIN, 'token', ADMIN_JWT)
        newest_event = Event.query.order_by(Event.id.desc()).first()
        res = self.client.get('/events/' + str(newest_event.id) + '/edit')
        self.assertEqual(res.status_code, 403)

    def test_edit_event(self):
        self.client.set_cookie(DOMAIN, 'token', MEMBER_JWT)
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

        self.app = create_app(test_config=None,database_path=TEST_DB_PATH)
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
