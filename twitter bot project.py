import tweepy
import tkinter as tk
from tkinter import Label, Entry, Button, messagebox, Checkbutton, BooleanVar

# API credentials from original code


class TwitterBot:
    def __init__(self, root):
        # Set up the GUI
        self.root = root
        self.root.title("Twitter Bot")
        self.root.geometry("400x400")
        
        # Bot configuration section
        Label(root, text="Bot Configuration", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        Label(root, text="Search Keyword:").pack()
        self.search_entry = Entry(root, bd=5, width=30)
        self.search_entry.pack()
        
        Label(root, text="Number of Tweets:").pack(pady=(5, 0))
        self.tweet_count_entry = Entry(root, bd=5, width=30)
        self.tweet_count_entry.pack()
        self.tweet_count_entry.insert(0, "10")  # Default value
        
        Label(root, text="Response Text:").pack(pady=(5, 0))
        self.response_entry = Entry(root, bd=5, width=30)
        self.response_entry.pack()
        
        # Create action checkboxes using variables
        self.should_reply = BooleanVar()
        self.should_retweet = BooleanVar()
        self.should_like = BooleanVar()
        self.should_follow = BooleanVar()
        
        Checkbutton(root, text="Reply to tweets", variable=self.should_reply).pack(pady=(5, 0))
        Checkbutton(root, text="Retweet", variable=self.should_retweet).pack()
        Checkbutton(root, text="Like tweets", variable=self.should_like).pack()
        Checkbutton(root, text="Follow users", variable=self.should_follow).pack()
        
        # Status message
        self.status_label = Label(root, text="Not connected", fg="red")
        self.status_label.pack(pady=(10, 0))
        
        # Action buttons
        Button(root, text="Connect to Twitter", command=self.connect_to_twitter).pack(pady=(10, 5))
        Button(root, text="Follow My Followers", command=self.follow_followers).pack(pady=(5, 5))
        Button(root, text="Start Bot", command=self.interact_with_tweets).pack(pady=5)
        
        # Initialize API client
        self.client = None
        self.api = None
    
    def connect_to_twitter(self):
        """Connect to Twitter API using provided credentials"""
        try:
            # Set up authentication for API v2
            self.client = tweepy.Client(
                bearer_token=None,  # We'll use OAuth 1.0a authentication
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            
            # Also set up v1.1 API for methods not available in v2
            auth = tweepy.OAuth1UserHandler(
                consumer_key, consumer_secret,
                access_token, access_token_secret
            )
            self.api = tweepy.API(auth)
            
            # Test the connection
            user_data = self.client.get_me()
            if user_data and user_data.data:
                username = user_data.data.username
                self.status_label.config(text=f"Connected as @{username}", fg="green")
                messagebox.showinfo("Success", f"Connected as @{username}")
            else:
                self.status_label.config(text="Connection failed", fg="red")
                messagebox.showerror("Error", "Failed to get user data")
        
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
    
    def follow_followers(self):
        """Follow users who follow you but you don't follow back"""
        if not self.client:
            messagebox.showerror("Error", "Please connect to Twitter first!")
            return
            
        try:
            # Get user ID
            me = self.client.get_me()
            user_id = me.data.id
            
            # Using v1.1 API for following followers (easier with this API)
            if self.api:
                follow_count = 0
                for follower in tweepy.Cursor(self.api.get_followers).items(100):
                    if not follower.following:
                        follower.follow()
                        follow_count += 1
                        print(f"Followed: @{follower.screen_name}")
                
                messagebox.showinfo("Success", f"Followed {follow_count} new followers")
            else:
                # Fallback to v2 API
                followers = self.client.get_users_followers(
                    id=user_id,
                    max_results=100
                )
                
                if not followers.data:
                    messagebox.showinfo("Info", "You don't have any followers yet!")
                    return
                    
                following = self.client.get_users_following(
                    id=user_id,
                    max_results=100
                )
                
                following_ids = [user.id for user in following.data] if following.data else []
                
                follow_count = 0
                for follower in followers.data:
                    if follower.id not in following_ids:
                        self.client.follow_user(follower.id)
                        follow_count += 1
                        print(f"Followed: @{follower.username}")
                
                messagebox.showinfo("Success", f"Followed {follow_count} new followers")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def interact_with_tweets(self):
        """Search for tweets and interact with them based on user configuration"""
        if not self.client:
            messagebox.showerror("Error", "Please connect to Twitter first!")
            return
            
        try:
            search_query = self.search_entry.get()
            if not search_query:
                messagebox.showerror("Error", "Please enter a search keyword!")
                return
                
            tweet_count = int(self.tweet_count_entry.get())
            response_text = self.response_entry.get()
            
            # Check if reply is selected but no response text provided
            if self.should_reply.get() and not response_text:
                messagebox.showerror("Error", "Response text is required when reply is enabled!")
                return
            
            processed = 0
            
            # Using v1.1 API for search (more flexible)
            if self.api:
                for tweet in tweepy.Cursor(self.api.search_tweets, q=search_query).items(tweet_count):
                    try:
                        username = tweet.user.screen_name
                        
                        # Like tweet
                        if self.should_like.get():
                            self.api.create_favorite(tweet.id)
                            print(f"Liked tweet by @{username}")
                        
                        # Retweet
                        if self.should_retweet.get():
                            self.api.retweet(tweet.id)
                            print(f"Retweeted tweet by @{username}")
                        
                        # Reply
                        if self.should_reply.get():
                            self.api.update_status(
                                status=f"@{username} {response_text}",
                                in_reply_to_status_id=tweet.id
                            )
                            print(f"Replied to @{username}")
                        
                        # Follow user
                        if self.should_follow.get() and not tweet.user.following:
                            self.api.create_friendship(tweet.user.id)
                            print(f"Followed @{username}")
                        
                        processed += 1
                        
                    except Exception as e:
                        print(f"Error processing tweet: {str(e)}")
            else:
                # Fallback to v2 API
                tweets = self.client.search_recent_tweets(
                    query=search_query,
                    max_results=min(100, tweet_count)
                )
                
                if not tweets.data:
                    messagebox.showinfo("Info", "No tweets found for this search query!")
                    return
                
                for tweet in tweets.data[:tweet_count]:
                    try:
                        user = self.client.get_user(id=tweet.author_id)
                        username = user.data.username if user.data else "unknown"
                        
                        # Like tweet
                        if self.should_like.get():
                            self.client.like(tweet.id)
                            print(f"Liked tweet by @{username}")
                        
                        # Retweet
                        if self.should_retweet.get():
                            self.client.retweet(tweet.id)
                            print(f"Retweeted tweet by @{username}")
                        
                        # Reply
                        if self.should_reply.get():
                            self.client.create_tweet(
                                text=f"@{username} {response_text}",
                                in_reply_to_tweet_id=tweet.id
                            )
                            print(f"Replied to @{username}")
                        
                        # Follow user
                        if self.should_follow.get():
                            self.client.follow_user(tweet.author_id)
                            print(f"Followed @{username}")
                        
                        processed += 1
                        
                    except Exception as e:
                        print(f"Error processing tweet: {str(e)}")
            
            messagebox.showinfo("Success", f"Successfully processed {processed} tweets!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TwitterBot(root)
    root.mainloop()
