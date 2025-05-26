import datetime
import tkinter as tk
from tkinter import ttk


# Class that inherits ttk.Label - used for displaying the fields in the calendar
#
# handles the changing of dates and proper conversions to string
class CalendarDay(ttk.Label) :
    def __init__(self, curr_month=0, day=1, month=0, year=1970, master=None, **kwargs) :
        super().__init__(master, text=str(day), width=5, anchor='e', justify='right')
        
        self.is_same_month = True if curr_month == month else False
        self.month = month
        self.day = day
        self.year = year
        
    def to_string(self, include_year=False) :
        return_string = '/'.join(['{:02d}'.format(self.day), '{:02d}'.format(self.month)])
        
        if include_year :
            return_string += f'/{self.year}'
            
        return return_string
    
    def set_date(self, curr_month=0, day=0, month=0, year=1970) :
        self.is_same_month = True if curr_month == month else False
        self.month = month
        self.day = day
        self.year = year
        
        self.config(text=str(self.day))
        
        

class Calendar(ttk.Frame) :
    def __init__(self, master=None, title='Calendar', padding=10, **kwargs) :
        super().__init__(master, padding=padding)
        self.master = master
        self.master.title(title)
        curr_time = datetime.datetime.today()
        self.month = curr_time.month
        self.year = curr_time.year

        self.read_holidays()
        self.define_frame_widgets()
    
    # Method that defines the widgets in the app
    def define_frame_widgets(self) :
        self.grid()

        # Define labels used in the top row of the calendar - day of week
        self.dow_labels = []
        days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
        for i, day in enumerate(days) :
            new_label = ttk.Label(self, text=day, width=5, anchor='e', justify='right')
            new_label.grid(column=i%7, row=2)
            self.dow_labels.append(new_label)
        
        # Define the labels for each calendar day
        self.date_labels = []
        for i in range(42) :
            new_label = CalendarDay(master=self)
            new_label.grid(column=i%7, row=i//7 + 3)
            self.date_labels.append(new_label)

        # Define combobox for month selection
        self.month_combobox = ttk.Combobox(self, width=16)
        self.month_combobox['values'] = ('January', 
                                  'February',
                                  'March',
                                  'April',
                                  'May',
                                  'June',
                                  'July',
                                  'August',
                                  'September',
                                  'October',
                                  'November',
                                  'December')
        
        # Handle initial combobox value and bind events to it
        self.month_combobox.current(self.month-1) 
        self.month_combobox.bind('<<ComboboxSelected>>', self.month_selection_event)
        self.month_combobox.grid(column=0, row=0, columnspan=4, sticky='W')

        # Define entry field for year selection + validation and event handling
        self.year_string_variable = tk.StringVar()
        self.year_string_variable.set(str(self.year))
        self.year_string_variable.trace('w',
                                        lambda name,
                                        index,
                                        mode,
                                        sv=self.year_string_variable: self.year_entry_event(self.year_string_variable))
        
        validation = (self.master.register(self.year_entry_validation))
        self.year_entry = tk.Entry(self,
                              textvariable=self.year_string_variable,
                              validate='all',
                              validatecommand=(validation, '%P'),
                              width=16)
        self.year_entry.grid(column=4, row=0, columnspan=3, sticky='E')
        
        # Define entry field for selection by date
        curr_time = datetime.datetime.today()
        self.date_string_variable = tk.StringVar()
        self.date_string_variable.set(curr_time.strftime('%d/%m/%Y'))
        self.date_string_variable.trace('w',
                                        lambda name,
                                        index,
                                        mode,
                                        sv=self.date_string_variable: self.date_entry_event(self.date_string_variable))
        
        self.date_entry = tk.Entry(self,
                                   textvariable=self.date_string_variable,
                                   width=16)
        self.date_entry.grid(column=4, row=1, columnspan=3, sticky='E')
        
        # Define label used for errors
        self.invalid_date_label = ttk.Label(self, text='Enter date: dd/mm/yyyy', foreground='gray')
        self.invalid_date_label.grid(column=0, row=1, columnspan=4, sticky='W')
        
        # Define 'Quit' button
        self.quit_button = ttk.Button(self,
                                      text='Quit',
                                      command=self.master.destroy)
        self.quit_button.grid(column=4, row=9, columnspan=3, sticky='E')
        
        # Initialise the data
        self.change_calendar_view()
    
    # Method used for reading the holidays from a txt file
    def read_holidays(self) :
        holidays_file = open('./data/holidays.txt', 'r')
        self.holidays = {}
        
        for holiday in holidays_file :
            holiday_data = holiday[:-1].split(',')
            if len(holiday_data) == 2 :
                repeating_flag = holiday_data[1]
                
                # if repeating - save the date without the year
                # save the year defined in the file - presumed to be the first
                # day on which the holiday was commemorated
                if repeating_flag == 'r' :
                    holiday_date = holiday_data[0].split('/')
                    
                    repeating_date = '/'.join(holiday_date[:2])
                    self.holidays[repeating_date] = int(holiday_date[2])
                
                # Otherwise save the date including the year
                elif repeating_flag == 'n' :
                    self.holidays[holiday_data[0]] = -1;
                                 
                    
                    
    # Year entry validation - numerical and shorter than 5 numbers
    def year_entry_validation(self, P) :
        return (str.isdigit(P) or P == '') and len(P) < 5
    
    # Handle the changes in the year entry field
    def year_entry_event(self, year_string_variable) :
        year = year_string_variable.get()
        
        if len(year) == 4 :
            self.change_year_and_month(int(year), self.month)
    
    # Handle the changes in the date selection entry field
    def date_entry_event(self, date_string_variable) :
        date_entry = date_string_variable.get()
        date_entry_split = date_entry.split('/')
        valid_date = False
        
        # Validate the input data
        if len(date_entry_split) == 3 :
            if (date_entry_split[0].isnumeric()
                and date_entry_split[1].isnumeric()
                and date_entry_split[2].isnumeric()) :
                
                day = int(date_entry_split[0])
                month =int(date_entry_split[1])
                year = int(date_entry_split[2])
                
                # Check if date exists, then change the calendar view
                if self.is_valid_date(year, month, day) :
                    self.change_year_and_month(year, month)
                    valid_date = True
        
        # Otherwise report an error
        if not valid_date :
            self.invalid_date_label['text'] = 'Date not valid.'
            self.invalid_date_label.config(foreground='red')
        else :
            self.invalid_date_label['text'] = 'Enter date: dd/mm/yyyy'
            self.invalid_date_label.config(foreground='gray')
        
    
    # Handle combobox option selection
    def month_selection_event(self, event) :
        month = self.month_combobox.current() + 1
        self.change_year_and_month(self.year, month)

    def is_valid_date(self, year, month, day):
        try:
            newDate = datetime.datetime(int(year), int(month), int(day))
            return True
        except ValueError:
            return False


    def change_year_and_month(self, year, month) :
        self.year = year
        self.month = month
        
        self.change_calendar_view()
        
    def change_calendar_view(self) :
        # Check the DOW of where the month begins and adjust the first date
        # displayed in the calendar accordingly
        curr_month_datetime = datetime.datetime(self.year, self.month, 1)
        first_of_month_weekday = curr_month_datetime.weekday()
        delta_start_of_calendar = datetime.timedelta(days = first_of_month_weekday)
        variable_datetime = curr_month_datetime - delta_start_of_calendar
        
        # Define step
        delta_one_day = datetime.timedelta(days = 1)

        for i, day_label in enumerate(self.date_labels) :
            # Change the date in the label
            day_label.set_date(self.month,
                         variable_datetime.day,
                         variable_datetime.month,
                         variable_datetime.year)
            
            variable_datetime = variable_datetime + delta_one_day
            
            # Check for holidays
            repeating_date = day_label.to_string(include_year=False)
            unique_date = day_label.to_string(include_year=True)
            is_holiday = False
            
            if repeating_date in self.holidays and self.holidays[repeating_date] <= day_label.year :
                    is_holiday = True
            elif unique_date in self.holidays :
                is_holiday = True
            
            # According to the DOW, holidays, and the current month
            # determine how the labels should be coloured
            if not day_label.is_same_month :
                if i % 7 == 6 or is_holiday:
                    day_label.config(foreground='salmon')
                else :
                    day_label.config(foreground='gray')
            elif i % 7 == 6 or is_holiday :
                day_label.config(foreground='red')
            else :
                day_label.config(foreground='black')
            
            
            
if __name__ == '__main__' :
    app = tk.Tk()
    calendar = Calendar(master=app)
    app.mainloop()

