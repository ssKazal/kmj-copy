# API Documentation
```
Some Api end require authentication token in request Header
```

### User Registrations
```
POST /user/registration/
	* From email and phone_number one field is required
	> username [text] (required)
	> email [email] 
	> phone_number [country code + phone number]
	> first_name [text] (required)
	> last_name [text] (required)
	> date_of_birth [date:YYYY-MM-DD] (required)
	> country [integer] (required)
	> city [text] (required)
	> profile_picture [file] (required)
	> age_consent [integer] (required)
	> password [password] (required)
	> confirm_password [password] (required)
	> terms_and_condition [boolean]
```

### Authentication
```
POST /api/login/
    > email [email/phone] (required)
    > password [password] (required)

POST /api/token/refresh_token/
	> refresh [text] (required)

```

### Account Verification
```
POST /user/send-verification-key/	[token required]
POST /user/verify-account/	[token required]
	> verification_key [token] (required)
```

### Reset Password
```
POST /user/reset-password-request/
	* between email/phone_number one is required
	> email [email]
	> phone_number [phone]
POST /user/reset-password/
	> verification_key [token] (required)
	> new_password [password] (required)
	> confirm_new_password [password] (required)

```

### Change Password
```
PUT /user/change_password/	[token required]
	> old_password [password] (required)
	> new_password [password] (required)
	> confirm_new_password [password] (required)

```

### User Profile
```
GET /user/user_customer_profile/	[token required]
GET /user/user_skilled_worker_profile/	[token required]
PUT/PATCH /user/update_profile/	[token required]
	> email [email]
	> phone_number [phone]
	> first_name [text] (required)
	> last_name [text] (required)
	> date_of_birth [date:yyyy-mm-dd] (required)
	> country [integer] (required)
	> city [text] (required)
	> profile_picture [file] (required)
	> age_consent [integer] (required)
	* To create 'SkilledWorker' profile 'occupation obj' and 'description' field is required and to update 'SkilledWorker' profile also 'experience' is required
	> occupation [integer] (required)
	> experience [float] (required)
	> description [text] (required)
	> terms_and_condition [boolean]
	> email_subscription [boolean]
```

### Certification
```
POST /certifications/	[token required]
	> certification_name [text] (required)
	> description [text] (required)
	> date_earned [date:YYYY-MM-DD] (required)
	> certification_issued [url]
GET /certifications/<certification_id>/	[token required]
PUT /certifications/<certification_id>/	[token required]
	> certification_name [text] (required)
	> description [text] (required)
	> date_earned [date:YYYY-MM-DD] (required)
	> certification_issued [url]
DELETE /certifications/<certification_id>/	[token required]
```

### SkilledWorker Profile
```
GET /skilledworkers/
	> country [integer] (exact)
	> city__icontains [text] (icontains)
	> occupation [text] (icontains)
GET /skilledworkers/<user_id>/
GET /skilledworkers/<user_id>/portfolio/
GET /skilledworkers/<user_id>/certifications/
```

### Favorite
```
POST /favorites/	[token required]
	> skilled_worker [integer] (required)
GET /favorites/<favorite_id>/	[token required]
PUT/PATCH /favorites/<favorite_id>/	[token required]
	> skilled_worker [integer]
DELETE /favorites/<favorite_id>/	[token required]
```

### Portfolio
```
GET /portfolios/	[token required]
GET /portfolios/<portfolio_id>/	[token required]
PUT/PATCH /portfolios/<portfolio_id>/	[token required]
	> education [text] (required)
	> description [text] (required)
	> certification [integer]
```

### PortfolioImage
```
GET /portfolios/portfolio-image/	[token required]
POST /portfolios/portfolio-image/	[token required]
	> picture [file] (required)
GET /portfolios/portfolio-image/<portfolio_image_id>/	[token required]
PUT/PATCH /portfolios/portfolio-image/<portfolio_image_id>/	[token required]
	> picture [file] (required)
DELETE /portfolios/portfolio-image/<portfolio_image_id>/	[token required]
```

### Contact Us
```
POST /contact-us/	[token required]
	> title [text] (required)
	> message [text] (required)
	> attachment [file]
```

### Notification
```
GET /notifications/ [token required]
GET /notifications/<notification_id>/ [token required]
PATCH /notifications/<notification_id>/mark_as_read/ [token required]
	> is_read [boolean]
```

