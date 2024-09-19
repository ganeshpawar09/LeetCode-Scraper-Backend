import sys
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from warnings import filterwarnings

filterwarnings('ignore')

class LeetcodeScraper:
    def __init__(self):
        self.base_url = 'https://leetcode.com/graphql'

    def scrape_user_profile(self, username):
        output = {}

        def scrape_single_operation(operation):
            json_data = {
                'query': operation_query_dict.get(operation, ''),
                'variables': {'username': username},
                'operationName': operation
            }

            if operation == 'recentAcSubmissions':
                json_data['variables']['limit'] = 15

            try:
                response = requests.post(self.base_url, json=json_data, stream=True, verify=False)
                response.raise_for_status()  # Raise an exception for HTTP errors
                response_data = response.json()
                output[operation] = response_data.get('data', {})
            except requests.exceptions.RequestException as e:
                print(f'username: {username}', f'operation: {operation}', f'error: {e}', sep='\n')

        operation_query_dict = {
            'userPublicProfile':'\n    query userPublicProfile($username: String!) {\n  matchedUser(username: $username) {\n    contestBadge {\n      name\n      expired\n      hoverText\n      icon\n    }\n    username\n    githubUrl\n    twitterUrl\n    linkedinUrl\n    profile {\n      ranking\n      userAvatar\n      realName\n      aboutMe\n      school\n      websites\n      countryName\n      company\n      jobTitle\n      skillTags\n      postViewCount\n      postViewCountDiff\n      reputation\n      reputationDiff\n      solutionCount\n      solutionCountDiff\n      categoryDiscussCount\n      categoryDiscussCountDiff\n    }\n  }\n}\n    ',
            'languageStats':'\n    query languageStats($username: String!) {\n  matchedUser(username: $username) {\n    languageProblemCount {\n      languageName\n      problemsSolved\n    }\n  }\n}\n    ',
            'skillStats':'\n    query skillStats($username: String!) {\n  matchedUser(username: $username) {\n    tagProblemCounts {\n      advanced {\n        tagName\n        tagSlug\n        problemsSolved\n      }\n      intermediate {\n        tagName\n        tagSlug\n        problemsSolved\n      }\n      fundamental {\n        tagName\n        tagSlug\n        problemsSolved\n      }\n    }\n  }\n}\n    ',
            'userProblemsSolved':'\n    query userProblemsSolved($username: String!) {\n  allQuestionsCount {\n    difficulty\n    count\n  }\n  matchedUser(username: $username) {\n    problemsSolvedBeatsStats {\n      difficulty\n      percentage\n    }\n    submitStatsGlobal {\n      acSubmissionNum {\n        difficulty\n        count\n      }\n    }\n  }\n}\n    ',
            'userBadges':'\n    query userBadges($username: String!) {\n  matchedUser(username: $username) {\n    badges {\n      id\n      name\n      shortName\n      displayName\n      icon\n      hoverText\n      medal {\n        slug\n        config {\n          iconGif\n          iconGifBackground\n        }\n      }\n      creationDate\n      category\n    }\n    upcomingBadges {\n      name\n      icon\n      progress\n    }\n  }\n}\n    ',
            'userProfileCalendar':'\n    query userProfileCalendar($username: String!, $year: Int) {\n  matchedUser(username: $username) {\n    userCalendar(year: $year) {\n      activeYears\n      streak\n      totalActiveDays\n      dccBadges {\n        timestamp\n        badge {\n          name\n          icon\n        }\n      }\n      submissionCalendar\n    }\n  }\n}\n    ',
            'recentAcSubmissions':'\n    query recentAcSubmissions($username: String!, $limit: Int!) {\n  recentAcSubmissionList(username: $username, limit: $limit) {\n    id\n    title\n    titleSlug\n    timestamp\n  }\n}\n    ',
        }

        with ThreadPoolExecutor(max_workers=len(operation_query_dict)) as executor:
            executor.map(scrape_single_operation, operation_query_dict)

        return output

    def _scrape_single_global_ranking_page(self, page_num, only_user_details=True):
        query = '''
        {
          globalRanking(page: %d) {
            totalUsers
            userPerPage
            rankingNodes {
              ranking
              currentRating
              currentGlobalRanking
              dataRegion
              user {
                username
                nameColor
                activeBadge {
                  displayName
                  icon
                }
                profile {
                  userAvatar
                  countryCode
                  countryName
                  realName
                }
              }
            }
          }
        }
        ''' % page_num
        try:
            response = requests.post(self.base_url, json={'query': query}, stream=True, verify=False)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json().get('data', {}).get('globalRanking', {})
            return data['rankingNodes'] if only_user_details else data
        except requests.exceptions.RequestException as e:
            print(f'Error in page number: {page_num}', f'Error: {e}', sep='\n')

    def scrape_all_global_ranking_users(self):
        first_response = self._scrape_single_global_ranking_page(1, only_user_details=False)
        if not first_response:
            return {'error': 'Failed to fetch global ranking data'}

        total_leetcode_global_ranking_users = first_response.get('totalUsers', 0)
        users_per_page = first_response.get('userPerPage', 0)
        total_global_ranking_pages = total_leetcode_global_ranking_users // users_per_page
        print(f'Total Leetcode users: {total_leetcode_global_ranking_users}', f'Users per page: {users_per_page}', f'Total pages: {total_global_ranking_pages}', sep='\n')

        final_response = first_response.get('rankingNodes', [])

        with ThreadPoolExecutor(max_workers=500) as executor:
            pages = range(2, total_global_ranking_pages + 1)
            results = executor.map(self._scrape_single_global_ranking_page, pages)
            for result in results:
                if result:
                    final_response.extend(result)
        
        return {
            'total_global_ranking_users_present': total_leetcode_global_ranking_users,
            'total_global_ranking_users_scraped': len(final_response),
            'total_global_ranking_pages': total_global_ranking_pages,
            'all_global_ranking_users': final_response
        }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scraper.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    scraper = LeetcodeScraper()
    result = scraper.scrape_user_profile(username)
    
    print(json.dumps(result))
