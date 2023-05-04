# Social Media API
This is a RESTful API for a social media platform built using Django REST framework. 
The API allows users to create profiles, follow other users, create and retrieve posts, manage likes and comments, and perform basic social media actions.

## How to run
```shell
git clone https://github.com/SafonovVladimir/social-media-api.git
cd social_media_api
python3 -m venv venv
source venv/bin/activete # for linux or macOS
venv\Scripts\activete # for Windows
```

 The API will be available at http://localhost:8000/.
 
## API Endpoints
The following endpoints are available:
### User Registration, Authentication and Following
- api/user/register: Register a new user by providing an email and password.
- api/user/token: Receive a token
- api/user/token/refresh/: Refresh a token
- api/user/token/verify/: Verify a token
- api/user/me/: User information
- api/user/<int:pk>/follow/: Follow/Unfollow another user by providing their user ID.

### Post Creation and Retrieval
- api/post/feed/: Retrieve a list of all posts.
- api/post/my-posts/: User's posts
- api/post/create/: Create a new post by providing text content and media attachments (optional).
- api/post/<int:pk>/like/: Like/Unlike a post by providing the ID of the post.
- api/post/liked/: Retrieve a list of all posts liked by the currently authenticated user.

### Documentations
- api/doc/swagger/: Documentations using Swagger