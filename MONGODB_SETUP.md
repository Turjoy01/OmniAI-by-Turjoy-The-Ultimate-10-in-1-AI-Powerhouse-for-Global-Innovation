# MongoDB Atlas Connection Setup

## How to Get Your MongoDB Atlas Connection String

1. **Log in to MongoDB Atlas**: Go to https://cloud.mongodb.com

2. **Navigate to your cluster**: Click on "Connect" button for your cluster

3. **Choose "Connect your application"**

4. **Copy the connection string**: It will look like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

5. **Replace placeholders**:
   - Replace `<username>` with your MongoDB Atlas username
   - Replace `<password>` with your MongoDB Atlas password
   - The cluster address (cluster0.xxxxx.mongodb.net) is already in the string

6. **Update your .env file**: Replace the MONGODB_URI line with your actual connection string

## Important: IP Whitelist

Make sure your IP address is whitelisted in MongoDB Atlas:
1. Go to "Network Access" in MongoDB Atlas
2. Click "Add IP Address"
3. Add `0.0.0.0/0` (allows all IPs) OR your specific IP address

## Example .env file format:

```
OPENAI_API_KEY=your_key_here
MONGODB_URI=mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=chatgpt_clone
COLLECTION_NAME=chat_sessions
```

**Note**: Make sure there are NO spaces around the `=` sign and NO quotes around the connection string.

