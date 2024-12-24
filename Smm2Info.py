import requests

class Smm2Info:
    BASE_URL = "https://tgrcode.com/mm2/"
    def __init__(self):
        pass

    def get_user(self, user_code:int|str)->dict[str, dict[str]]|None:
        response = requests.get(self.BASE_URL + f"user_info/{user_code}")
        data = {}
        if response.status_code == 200:
            res = response.json()
            data['user'] = {
                'region': res['region'],
                'code': res['code'],
                'name': res['name'],
                'country': res['country'],
                'mii_image': str(res['mii_image']),
                'courses_played': res['courses_played'],
                'courses_cleared': res['courses_cleared'],
                'courses_attempted': res['courses_attempted'],
                'courses_deaths': res['courses_deaths'],
                'likes': res['likes'],
                'maker_points': res['maker_points'],
                'easy_highscore': res['easy_highscore'],
                'normal_highscore': res['normal_highscore'],
                'expert_highscore': res['expert_highscore'],
                'super_expert_highscore': res['super_expert_highscore'],
                'weekly_maker_points': res['weekly_maker_points'],
            }
            data['versus'] = {
                'rating': res['versus_rating'],
                'rank': res['versus_rank'],
                'rank_name': res['versus_rank_name'],
                'won': res['versus_won'],
                'lost': res['versus_lost'],
                'win_streak': res['versus_win_streak'],
                'lose_streak': res['versus_lose_streak'],
                'plays': res['versus_plays'],
                'disconnected': res['versus_disconnected'],
            }
            data['coop'] = {
                'clears': res['coop_clears'],
                'plays': res['coop_plays'],
            }
          
            data['first_clears'] = res.get('first_clears', None)
            data['world_records'] = res.get('world_records', None)
            data['unique_super_world_clears'] = res.get('unique_super_world_clears', None)
            data['uploaded_levels'] = res.get('uploaded_levels', None)
            data['comments_enabled'] = res.get('comments_enabled', None)
            data['tags_enabled'] = res.get('tags_enabled', None)
            data['super_world_id'] = res.get('super_world_id', None)
            data['badges'] = res.get('badges', None)
            
        else:
            return None
        
        return data

    def get_level(self,level_code:int|str)->dict[str, dict[str]]|None:
        response = requests.get(self.BASE_URL + f"level_info/{level_code}")
        data = {}
        if response.status_code == 200:
            res = response.json()
            data['level'] = {
                'name': res['name'],
                'description': res['description'],
                'uploaded': res['uploaded'],
                'code': res['course_id'],
                'game_style_name': res['game_style_name'],
                'theme_name': res['theme_name'],
                'difficulty_name': res['difficulty_name'],
                'tags_name': res['tags_name'],
                'world_record': res['world_record'],
                'upload_time': res['upload_time'],
                'num_comments': res['num_comments'],
                'clear_condition': res['clear_condition'],
                'clear_condition_magnitude': res['clear_condition_magnitude'],
                'clears': res['clears'],
                'attempts': res['attempts'],
                'clear_rate': res['clear_rate'],
                'plays': res['plays'],
                'versus_matches': res['versus_matches'],
                'coop_matches': res['coop_matches'],
                'likes': res['likes'],
                'boos': res['boos'],
                'unique_players_and_versus': res['unique_players_and_versus'],
                'weekly_likes': res['weekly_likes'],
                'weekly_plays': res['weekly_plays'],
                'one_screen_thumbnail_url': f'{self.BASE_URL}level_thumbnail/{level_code}',
            }
            data['creator']={
                'region': res['uploader']['region_name'],
                'code': res['uploader']['code'],
                'name': res['uploader']['name'],
                'country': res['uploader']['country'],
                'mii_image': res['uploader']['mii_image'],
            }
            data['first_completer']={
                'region': res['first_completer']['region_name'],
                'code': res['first_completer']['code'],
                'name': res['first_completer']['name'],
                'country': res['first_completer']['country'],
                'mii_image': res['first_completer']['mii_image'],
            }
            data['record_holder']={
                'region': res['record_holder']['region_name'],
                'code': res['record_holder']['code'],
                'name': res['record_holder']['name'],
                'country': res['record_holder']['country'],
                'mii_image': res['record_holder']['mii_image'],
            }
            
        else:
            return None
        
        return data


if __name__ == '__main__':
    smm2 = Smm2Info()
    PascalA79 = smm2.get_user('8SB-KPY-7JF')
    the_pik_pik_challenge = smm2.get_level('Q8C-W2D-GDG')
    print(PascalA79)
    print(the_pik_pik_challenge)