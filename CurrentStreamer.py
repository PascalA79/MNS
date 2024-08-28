class CurrentStreamer:
    def __init__(self, streamer_data:dict= None) -> None:
        if streamer_data == None:
            streamer_data = {}
        self.name = streamer_data.get('user_name')
        self.id_twitch = streamer_data.get('user_id')
        self.title = streamer_data.get('title')
        self.description = streamer_data.get('description')
        self.game = streamer_data.get('game_name')
        self.game_id = streamer_data.get('game_id')
        self.viewer_count = streamer_data.get('viewer_count')
        self.started_at = streamer_data.get('started_at')
        self.thumbnail_url = streamer_data.get('thumbnail_url')
        self.url = f"https://www.twitch.tv/{self.name}" if self.name else None
        self.description = streamer_data.get('description')
        self.stream_id = streamer_data.get('id')