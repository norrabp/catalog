import unittest
from werkzeug.exceptions import NotFound, BadRequest
from pymysql import err
from app import create_app, db, ValidationError
from app.models import User
from .test_client import TestClient


class TestAPI(unittest.TestCase):
    default_username = 'GotIt'
    default_password = 'GotItAI'

    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        u = User(username=self.default_username)
        u.set_password(self.default_password)
        db.session.add(u)
        db.session.commit()
        self.client = TestClient(self.app, u.generate_auth_token(), '')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def testCategories(self):
        # Get empty list of categories
        rv, json = self.client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 0)

        # Create categories
        rv, json = self.client.post('/api/v1/categories', data={'name': 'Basketball'})
        self.assertTrue(rv.status_code == 201)
        cat_id = rv.headers['id']
        rv, json = self.client.get('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Basketball')
        rv, json = self.client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 1)

        # Edit categories
        rv, json = self.client.put('/api/v1/categories/' + str(cat_id), data={'name': 'Baseball'})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Baseball')
        rv, json = self.client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 1)

        # Delete category
        rv, json = self.client.delete('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 204)
        rv, json = self.client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 0)

    def testItems(self):
        # Create a category
        rv, json = self.client.post('/api/v1/categories', data={'name': 'Baseball'})
        self.assertTrue(rv.status_code == 201)
        cat_id = int(rv.headers['id'])
        rv, json = self.client.get('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Baseball')
        rv, json = self.client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 1)

        # Get empty list of items
        rv, json = self.client.get('/api/v1/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['items']) == 0)
        rv, json = self.client.get('/api/v1/categories/' + str(cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseball items']) == 0)

        # Create an item
        rv, json = self.client.post('/api/v1/categories/' + str(cat_id) + '/items',
                                    data={'title': 'Bat',
                                          'description': "The batter uses this to hit the baseball"})
        self.assertTrue(rv.status_code == 201)
        item_id = rv.headers['id']
        # Check the new item
        rv, json = self.client.get('/api/v1/items/' + item_id)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == 'Bat')
        self.assertTrue(json['category'] == cat_id)
        self.assertTrue(json['description'] == "The batter uses this to hit the baseball")
        # Check the category for that item
        rv, json = self.client.get('/api/v1/categories/' + str(cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseball items']) == 1)
        # Check the list of items
        rv, json = self.client.get('/api/v1/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['items']) == 1)

        # Edit an item's name and description
        rv, json = self.client.put('/api/v1/items/' + item_id,
                                   data={'title': "glove",'description': "Used by fielders to pick up"
                                                                         " the baseball"})
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == 'glove')
        self.assertTrue(json['description'] == "Used by fielders to pick up the baseball")
        # Edit only an item's name
        rv, json = self.client.put('/api/v1/items/' + item_id, data={'title': "Firstbaseman's Mitt"})
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == "Firstbaseman's Mitt")
        self.assertTrue(json['description'] == "Used by fielders to pick up the baseball")
        self.assertTrue(json['category'] == cat_id)
        # Edit only an item's description
        rv, json = self.client.put('/api/v1/items/' + item_id, data={'description': "Special glove used by the"
                                                                             " firstbaseman"})
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == "Firstbaseman's Mitt")
        self.assertTrue(json['description'] == "Special glove used by the firstbaseman")
        self.assertTrue(json['category'] == cat_id)

        # Move the item to a new category
        rv, json = self.client.post('/api/v1/categories', data={'name': 'Baseketball'})
        self.assertTrue(rv.status_code == 201)
        new_cat_id = int(rv.headers['id'])
        rv, json = self.client.get('/api/v1/categories/' + str(new_cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Baseketball')
        rv, json = self.client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 2)
        rv, json = self.client.put('/api/v1/items/' + item_id, data={'category': new_cat_id})
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == "Firstbaseman's Mitt")
        self.assertTrue(json['description'] == "Special glove used by the firstbaseman")
        self.assertTrue(json['category'] == new_cat_id)
        # Verify the new category has the item in it
        rv, json = self.client.get('/api/v1/categories/' + str(new_cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseketball items']) == 1)
        # Verify the old category has no items
        rv, json = self.client.get('/api/v1/categories/' + str(cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseball items']) == 0)

        # Delete the item
        rv, json = self.client.delete('/api/v1/items/' + item_id)
        self.assertTrue(rv.status_code == 204)
        rv, json = self.client.get('/api/v1/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['items']) == 0)
        rv, json = self.client.get('/api/v1/categories/' + str(new_cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseketball items']) == 0)

    def testErrors(self):

        # Test 400
        # self.assertRaises(ValidationError, self.client.post, '/api/v1/categories', data={})

        rv, json = self.client.post('/api/v1/categories', data={'name': "Baseball"})
        self.assertTrue(rv.status_code == 201)
        cat_id = int(rv.headers['id'])
        self.assertRaises((ValidationError, BadRequest), self.client.put, '/api/v1/categories/' + str(cat_id), data={})
        self.assertRaises((BadRequest, ValidationError), lambda: self.client.post('/api/v1/categories/' + str(cat_id) + '/items',
                                                                    data={'title': 'Bat'}))
        self.assertRaises((BadRequest, ValidationError), lambda: self.client.post('/api/v1/categories/' + str(cat_id) + '/items',
                                                                    data={'description': "Hits the ball"}))
        
        self.assertRaises((BadRequest, ValidationError), self.client.post, '/api/v1/categories/' + str(cat_id) + '/items', data={})
        rv, json = self.client.post('/api/v1/categories/' + str(cat_id) + '/items',
                                    data={'title': 'Bat', 'description': "Hits the ball"})
        self.assertTrue(rv.status_code == 201)
        item_id = int(rv.headers['id'])

        '''
        # Test 500 
        self.assertRaises(err.IntegrityError, lambda: self.client.post('/api/v1/categories',
                                                                   data={'name': 'Baseball'}))
        self.assertRaises(err.IntegrityError, lambda: self.client.post('/api/v1/categories' + str(cat_id) + '/items',
                                                                   data={'title': 'Bat'}))
        '''

        # Test 404
        self.assertRaises(NotFound, lambda: self.client.get('/api/v1/categories/'))
        self.assertRaises(NotFound, lambda: self.client.get('/api/v1/items/'))
        self.assertRaises(NotFound, lambda: self.client.get('/api/v1/categories/1234'))
        self.assertRaises(NotFound, lambda: self.client.get('/api/v1/categories/1234/items'))
        self.assertRaises(NotFound, lambda: self.client.get('/api/v1/items/1234'))
        rv, json = self.client.delete('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 204)
        self.assertRaises(NotFound, self.client.get, '/api/v1/items/' + str(item_id))
        rv, json = self.client.delete('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 204)
        self.assertRaises(NotFound, self.client.get, '/api/v1/categories/' + str(cat_id))

    def testUser(self):
        # Add some data to try and modify with another user
        rv, json = self.client.post('/api/v1/categories', data={'name': 'Baseball'})
        self.assertTrue(rv.status_code == 201)
        cat_id = int(rv.headers['id'])
        rv, json = self.client.post('/api/v1/categories/' + str(cat_id) + '/items',
                                    data={'title': "Bat", 'description': "What you hit the ball with"})
        self.assertTrue(rv.status_code == 201)
        item_id = int(rv.headers['id'])

        # Create an empty user, should be able to get but not anything else
        new_client = TestClient(self.app, '', '')
        rv, json = new_client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        rv, json = new_client.get('api/v1/items')
        self.assertTrue(rv.status_code == 200)
        # Try and fail to create a category
        rv, json = new_client.post('/api/v1/categories', data={'name': 'Soccer'})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 1)
        # Try and fail to edit a category
        rv, json = new_client.put('/api/v1/categories/' + str(cat_id), data={'name': 'Soccer'})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Baseball')
        # Try and fail to delete a category
        rv, json = new_client.delete('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Baseball')
        # Try and fail to create an item
        rv, json = new_client.post('/api/v1/categories/' + str(cat_id) + '/items',
                                   data={'title': 'Glove', 'description': "Fielders use this to catch the ball"})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['items']) == 1)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseball items']) == 1)
        # Try and fail to edit the item
        rv, json = new_client.put('/api/v1/items/' + str(item_id),
                                  data={'title': 'Glove', 'description': "Fielders use this to catch the ball"})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == 'Bat')
        self.assertTrue(json['description'] == "What you hit the ball with")
        # Try and fail to delete an item
        rv, json = new_client.delete('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == 'Bat')
        self.assertTrue(json['description'] == "What you hit the ball with")

        # Create a user with an unregistered username and password
        new_client = TestClient(self.app, 'patrick', 'cool')
        rv, json = new_client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        rv, json = new_client.get('api/v1/items')
        self.assertTrue(rv.status_code == 200)
        # Try and fail to create a category
        rv, json = new_client.post('/api/v1/categories', data={'name': 'Soccer'})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 1)
        # Try and fail to edit a category
        rv, json = new_client.put('/api/v1/categories/' + str(cat_id), data={'name': 'Soccer'})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Baseball')
        # Try and fail to delete a category
        rv, json = new_client.delete('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Baseball')
        # Try and fail to create an item
        rv, json = new_client.post('/api/v1/categories/' + str(cat_id) + '/items',
                                   data={'title': 'Glove', 'description': "Fielders use this to catch the ball"})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['items']) == 1)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseball items']) == 1)
        # Try and fail to edit the item
        rv, json = new_client.put('/api/v1/items/' + str(item_id),
                                  data={'title': 'Glove', 'description': "Fielders use this to catch the ball"})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == 'Bat')
        self.assertTrue(json['description'] == "What you hit the ball with")
        # Try and fail to delete an item
        rv, json = new_client.delete('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == 'Bat')
        self.assertTrue(json['description'] == "What you hit the ball with")

        # Create a user and register username and password, but don't get a new token
        u = User(username='patrick')
        u.set_password('cool')
        db.session.add(u)
        db.session.commit()
        new_client = TestClient(self.app, 'patrick', 'cool')
        rv, json = new_client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        rv, json = new_client.get('api/v1/items')
        self.assertTrue(rv.status_code == 200)
        # Try and fail to create a category
        rv, json = new_client.post('/api/v1/categories', data={'name': 'Soccer'})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 1)
        # Try and fail to edit a category
        rv, json = new_client.put('/api/v1/categories/' + str(cat_id), data={'name': 'Soccer'})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Baseball')
        # Try and fail to delete a category
        rv, json = new_client.delete('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Baseball')
        # Try and fail to create an item
        rv, json = new_client.post('/api/v1/categories/' + str(cat_id) + '/items',
                                   data={'title': 'Glove', 'description': "Fielders use this to catch the ball"})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['items']) == 1)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseball items']) == 1)
        # Try and fail to edit the item
        rv, json = new_client.put('/api/v1/items/' + str(item_id),
                                  data={'title': 'Glove', 'description': "Fielders use this to catch the ball"})
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == 'Bat')
        self.assertTrue(json['description'] == "What you hit the ball with")
        # Try and fail to delete an item
        rv, json = new_client.delete('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 401)
        rv, json = new_client.get('/api/v1/items/' + str(item_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == 'Bat')
        self.assertTrue(json['description'] == "What you hit the ball with")

        # Create client with token, all actions should be allowed
        new_client = TestClient(self.app, u.generate_auth_token(), '')
        # Successfully create a new category
        rv, json = new_client.post('/api/v1/categories', data={'name': 'Soccer'})
        self.assertTrue(rv.status_code == 201)
        new_cat_id = int(rv.headers['id'])
        rv, json = new_client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 2)
        # Successfully edit a category
        rv, json = new_client.put('/api/v1/categories/' + str(new_cat_id), data={'name': 'Basketball'})
        self.assertTrue(rv.status_code == 200)
        rv, json = new_client.get('/api/v1/categories/' + str(new_cat_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'Basketball')
        # Successfully delete a category
        rv, json = new_client.delete('/api/v1/categories/' + str(new_cat_id))
        self.assertTrue(rv.status_code == 204)
        rv, json = new_client.get('/api/v1/categories')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['categories']) == 1)
        # Successfully create an item
        rv, json = new_client.post('/api/v1/categories/' + str(cat_id) + '/items',
                                   data={'title': 'Glove', 'description': "Fielders use this to catch the ball"})
        self.assertTrue(rv.status_code == 201)
        new_item_id = int(rv.headers['id'])
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseball items']) == 2)
        rv, json = new_client.get('/api/v1/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['items']) == 2)
        # Successfully edit an item
        rv, json = new_client.put('/api/v1/items/' + str(new_item_id),
                                  data={'title': 'Helmet', 'description': "Used to protect the batter's head"})
        self.assertTrue(rv.status_code == 200)
        rv, json = new_client.get('/api/v1/items/' + str(new_item_id))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['title'] == 'Helmet')
        self.assertTrue(json['description'] == "Used to protect the batter's head")
        # Successfully delete an item
        rv, json = new_client.delete('/api/v1/items/' + str(new_item_id))
        self.assertTrue(rv.status_code == 204)
        rv, json = new_client.get('/api/v1/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['items']) == 1)
        rv, json = new_client.get('/api/v1/categories/' + str(cat_id) + '/items')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['Baseball items']) == 1)


if __name__ == '__main__':
    unittest.main()

