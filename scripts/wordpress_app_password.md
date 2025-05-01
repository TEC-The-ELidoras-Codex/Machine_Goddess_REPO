# How to Get a WordPress.com Application Password

Since you're using a WordPress.com site, you need to use a WordPress.com Application Password for API authentication.

## Step 1: Access Your WordPress.com Account Settings
1. Log in to WordPress.com
2. Go to your Account Settings (click on your profile image in the top-right corner)

## Step 2: Generate an Application Password
1. Navigate to **Security → Application Passwords**
2. Click on "Create an Application Password"
3. Name it "Machine Goddess Agent" or something similar
4. Copy the generated password immediately (it will be shown only once)

## Step 3: Update Your .env File
1. Open your `.env` file in the `config` directory
2. Update the WordPress credentials:
```
WP_USER=Elidorascodex
WP_APP_PASS=your_generated_application_password
```

## Step 4: Test Your Connection
Run the test script to verify your connection:
```
python scripts/test_wordpress_connection.py
```

## Important Notes:
- Application passwords are different from your WordPress.com account password
- They provide limited access to specific API functionality
- They're ideal for automated tools like your agents
- If you ever need to revoke access, you can delete the application password from your WordPress.com security settings

## Alternative: WordPress REST API Authentication Plugin
If you're still experiencing issues with authentication after getting an application password, you might need to:

1. Check if your WordPress.com plan supports the REST API features you're using
2. Consider upgrading your WordPress.com plan if needed for full REST API access
3. Use the REST API Authentication plugin from miniOrange if you have a Business plan or higher

Remember that WordPress.com has different REST API access levels based on your plan type.