from modules.interfaces.ICommand import ICommand
import datetime


class TopicTimetableCommand(ICommand):

    def __init__(self, group_id, account):
        super().__init__()
        self._triggers = ['t', 'T']
        self._extra_triggers = ['tt', 'Tt']
        self._days = []
        self._account = account
        self._group_id = group_id
        self.add_activate_time('6:00', '20:00')
        self.update()

    def proceed(self, user_id, command):
        if command in self._triggers:
            return self.get_short_timetable()
        if command in self._extra_triggers:
            return self.get_full_timetable()

    def setup_bot_account(self, account):
        self._account = account

    def update(self):
        if self._account is None:
            raise ValueError('BotAccount does not defined')
        self.parse_all_week(self.find_timetable_topic_id(self._group_id))

    def find_timetable_topic_id(self, group_id):
        topics = self._account.method('board.getTopics', {
            'group_id': group_id,
            'preview': 1,
            'preview_length': 0,
            'order': 2
        })
        items = topics.get('items')
        timetable_title = ['Расписание', 'Timetable']
        for topic in items:
            if topic.get('title') in timetable_title:
                return topic.get('id')

    def parse_all_week(self, topic_id):
        self._days = []
        comments = self._account.method('board.getComments', {
            'group_id': self._group_id,
            'topic_id': topic_id,
            'count': 6
        })
        for comment in comments.get('items'):
            text = comment.get('text')
            self._days.append(text)

    def get_full_timetable(self):
        timetable = ''
        for day in self._days:
            timetable += day + '\n' * 2
        return timetable

    def get_short_timetable(self):
        today = datetime.datetime.today().timetuple()
        wday = today.tm_wday
        if today.tm_hour < 13:
            return self._days[wday]
        else:
            return self._days[self.inc_day(wday)]

    def inc_day(self, today):
        if today in [5, 6]:
            return 0
        return today+1