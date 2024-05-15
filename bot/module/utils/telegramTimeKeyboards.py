from telegram import InlineKeyboardMarkup, InlineKeyboardButton

class telegramTimeKeyboards:
    @staticmethod
    def get_week_days_keyboard(start_day: int = 0, end_day: int = 7, days: list = None) -> InlineKeyboardMarkup:
        """
        Returns a keyboard with the days of the week starting from start_day and ending at end_day.
        start_day and end_day are 1-based indexes.
        params:
        start_day: int, default 0
        end_day: int, default 7
        days: list, default None (used for custom days names)
        """
        if days is None or len(days) != 7:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        daysKeyboard = [[InlineKeyboardButton(day, callback_data=day)] for day in days]
        # remove days before start_day
        #daysKeyboard = daysKeyboard[start_day - 1:]

        # remove days after end_day
        daysKeyboard = daysKeyboard[:end_day]

        daysKeyboard.append([InlineKeyboardButton("Cancel", callback_data="/cancel")])
        return InlineKeyboardMarkup(daysKeyboard)
    
    @staticmethod
    def get_hours_keyboard(start_hour: int = 0, end_hour: int = 23) -> InlineKeyboardMarkup:
        hoursKeyboard = []
        for hour in range(start_hour, end_hour + 1, 3):
            row = [InlineKeyboardButton(f"{hour:02d}", callback_data=f"{hour:02d}")]
            if hour + 1 <= end_hour:
                row.append(InlineKeyboardButton(f"{hour + 1:02d}", callback_data=f"{hour + 1:02d}"))
            if hour + 2 <= end_hour:
                row.append(InlineKeyboardButton(f"{hour + 2:02d}", callback_data=f"{hour + 2:02d}"))
            hoursKeyboard.append(row)
        hoursKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
        return InlineKeyboardMarkup(hoursKeyboard)

    @staticmethod
    def get_hours_partitions_keyboard(step: int) -> InlineKeyboardMarkup:
        # quartersKeyboard = [
        #     [InlineKeyboardButton("00", callback_data="00"), InlineKeyboardButton("15", callback_data="15")], 
        #     [InlineKeyboardButton("30", callback_data="30"), InlineKeyboardButton("45", callback_data="45")]
        # ]
        partitionsKeyboard = []
        for partition in range(0, 60, step):
            partitionsKeyboard.append([InlineKeyboardButton(f"{partition:02d}", callback_data=f"{partition:02d}")])

        partitionsKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
        return InlineKeyboardMarkup(partitionsKeyboard)