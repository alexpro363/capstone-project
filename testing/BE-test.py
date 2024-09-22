from database import query_exists, insert_query
import database

def main():
    user_search = input("Search Product: ")

    if query_exists(user_search):
        query_id = get_query_id(user_search)

    


if __name__ == "__main__":
    main()