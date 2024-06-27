from roapi import RobloxUser, GamePassCreator, RobloxGroups

def main():
    # Cookie information to authenticate with Roblox (replace <your_cookie_value> with your actual cookie)
    cookie = "<your_cookie_value>"
    
    # Creating instances of the classes for usage examples
    roblox_user = RobloxUser(cookie)
    game_pass_creator = GamePassCreator(cookie)
    roblox_groups = RobloxGroups(cookie, group_id=12345678)  # Group ID is required

    # Example usages
    print("--- Buying a Game Pass and Deleting it ---")
    roblox_user.buy(delete_after_purchase=True, id=98765432, type="pass")

    print("\n--- Creating a New Game Pass and Putting it on Sale ---")
    pass_id = game_pass_creator.create_pass(amount=50)
    if pass_id != "error":
        print(f"New Game Pass created with ID: {pass_id}")

    print("\n--- Taking a Game Pass Off Sale ---")
    game_pass_creator.take_off_sale(pass_id)

    print("\n--- Retrieving Group Revenue Summary ---")
    revenue_summary = roblox_groups.revenue_summary(time="day")
    print("Group Revenue Summary:", revenue_summary)

    print("\n--- Giving a Role to a User in the Group ---")
    response = roblox_groups.give_rank(role_id=3, username="example_user")
    print("Give Rank Response:", response)

    print("\n--- Listing Roles in the Group ---")
    roles = roblox_groups.list_roles()
    print("Group Roles:", roles)

if __name__ == "__main__":
    main()
