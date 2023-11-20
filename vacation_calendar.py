import streamlit as st
import pandas as pd
from datetime import date
from datetime import datetime
import calendar
import emoji
import redis


pool = redis.ConnectionPool(host = "192.168.23.80", port = 7777, db = 6, password = "uQ7nCNTvtpdPR9r2yEGL5qzZkmWDF8Xg")
r = redis.Redis(connection_pool= pool)

st.set_page_config(layout="wide")
page_bg_img = '''
<style>
.stApp {
background: linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(255,255,255,1) 75%, #26E544 100%);
}
</style>
<meta name="apple-mobile-web-app-capable" content="yes">
'''
st.markdown(page_bg_img, unsafe_allow_html=True)
font_css = """
<style>
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
  font-size: 16px;
}
</style>
"""
st.write(font_css, unsafe_allow_html=True)

st.markdown("""
    <style>
        [data-testid=stSidebar] {
            background-color: #90EE90;
        }
    </style>
    """, unsafe_allow_html=True)

leaders, calendar2 = st.tabs(['**Календарь отпусков сотрудников**','**Производственный календарь**'])

def get_structure(key, root=None) -> dict:
    """
    Функция `get_structure` извлекает структуру JSON из базы
        данных Redis, используя заданный ключ.

    @param key Параметр `key` представляет собой строку,
        представляющую ключ, используемый для
        извлечения данных из базы данных Redis.

    @return Функция `get_structure` возвращает словарь.
    """

    with redis.Redis(
        host = "192.168.23.80", port = 7777, db = 6, password = "uQ7nCNTvtpdPR9r2yEGL5qzZkmWDF8Xg"
    ) as redis_conn:  # Подключение Redis
        if root:
            res = redis_conn.json().get(key, root)
        else:
            res = redis_conn.json().get(key)


        if res:
            return res

if 'vcj' not in st.session_state:
      st.session_state.vcj = get_structure('vacation_calendar_yaskovich')
if 'elj' not in st.session_state:
      st.session_state.elj = get_structure('employees_list_yaskovich')
if 'edfj' not in st.session_state:
      st.session_state.edfj = get_structure('employees_data_frame_yaskovich')
if 'edij' not in st.session_state:
      st.session_state.edij = get_structure('employees_data_info_yaskovich')

if st.session_state.edfj is None:
      st.session_state.edfj = {}
if st.session_state.edij is None:
      st.session_state.edij = {}

def df_month_year(year, month):
  week_days = {0:'Понедельник',1:'Вторник',2:'Среда',3:'Четверг',4:'Пятница',5:'Суббота',6:'Воскресенье'}
  import datetime, calendar, pandas as pd
  dates = []
  for i in range(1,32):
        try:
              dates.append(datetime.date(year, month, i))
        except:
              pass
  dates = [(item.strftime('%d.%m.%Y'), item.isocalendar()[1], item.weekday()) for item in dates]
  ndates = [dates[0][1]]
  for item in dates:
        if not item[1] in ndates:
              ndates.append(item[1])
  wks = [item for item in ndates]
  df = []
  for w in wks:
        df.append([])
        for d in dates:
              if w == d[1]:
                    df[-1].append({week_days[d[2]]:d[0][:2]})
  df[0] = ['1']*(7-len(df[0])) + df[0]
  df[-1] = df[-1] + ['1']*(7-len(df[-1]))
  return df

def del_sotrudnik(sotrudnik):
      del st.session_state.elj['Список сотрудников'][select_depart1][st.session_state.elj['Список сотрудников'][select_depart1].index(sotrudnik)]
      r.json().set('employees_list_yaskovich', '$', st.session_state.elj)
      try:
            del st.session_state.edfj[select_depart1][employee_selection_leaders + '_' + str(select_year - 1)]
            del st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year - 1)]
      except:
            pass
      try:
            del st.session_state.edfj[select_depart1][employee_selection_leaders + '_' + str(select_year)]
            del st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)]
      except:
            pass
      try:
            del st.session_state.edfj[select_depart1][employee_selection_leaders + '_' + str(select_year + 1)]
            del st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year + 1)]
      except:
            pass
      r.json().set('employees_data_frame_yaskovich', '$', st.session_state.edfj)
      r.json().set('employees_data_info_yaskovich', '$', st.session_state.edij)
      r.json().set('employees_list_yaskovich', '$', st.session_state.elj)
      return
def add_sotrudnik(sotrudnikadd):
      st.session_state.elj['Список сотрудников'][select_depart1].append(sotrudnikadd)
      r.json().set('employees_list_yaskovich', '$', st.session_state.elj)
      return 

with st.sidebar:
      week_days = {0:'Понедельник',1:'Вторник',2:'Среда',3:'Четверг',4:'Пятница',5:'Суббота',6:'Воскресенье'}   
      head_cols = st.columns(1)
      try:
            if datetime.now().year - 1 in st.session_state.vcj:
                  select_year_list = [datetime.now().year - 1, datetime.now().year, datetime.now().year + 1]
            else:
                  select_year_list = [datetime.now().year, datetime.now().year + 1]
      except:
            pass
      select_year = head_cols[0].selectbox('Выберите год', select_year_list)
      select_depart_list = ['Руководители','Отдел поддержки продаж','Отдел сервиса','Техн. отдел по не стн.обор.','Техн. отдел по стн.обор.','Техн. отдел по автоматике']
      select_op1_depart_list = ['МСК-1','МСК-2','МСК-3']
      select_op2_depart_list = ['МСК-4','МСК-5','МСК-6']
      select_type_calendar = head_cols[0].selectbox('Календарь', ['Веза ЦЕНТР','ОП1','ОП2'])
      date_month_list = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
      date_month_nomer = {'Январь':1,'Февраль':2,'Март':3,'Апрель':4,'Май':5,'Июнь':6,'Июль':7,'Август':8,'Сентябрь':9,'Октябрь':10,'Ноябрь':11,'Декабрь':12}
      depart_type = {'Веза ЦЕНТР':'Отдел','ОП1':'МСК','ОП2':'МСК'}
      depart_type_list = {'Веза ЦЕНТР':select_depart_list,'ОП1':select_op1_depart_list,'ОП2':select_op2_depart_list}
      def names_depart_employes_list(selectdepart):
            return st.session_state.elj['Список сотрудников'][selectdepart]

      select_depart1 = head_cols[0].selectbox(depart_type[select_type_calendar], depart_type_list[select_type_calendar], key='sd1')
      max_worker = len(names_depart_employes_list(select_depart1))
      employee_selection_leaders = head_cols[0].selectbox(f'Выбор сотрудника из отдела {select_depart1}', names_depart_employes_list(select_depart1))
      list_sotrud = head_cols[0].toggle('**Список сотрудников**', key='ls1')

      if list_sotrud:
            for i in range(len(names_depart_employes_list(select_depart1))):
                  name = head_cols[0].caption(f':blue[{str(names_depart_employes_list(select_depart1)[i])}]')
      del_sotrudnik_on = head_cols[0].toggle('**Удаление сотрудника из списка**', key='leaders1')
      if del_sotrudnik_on:
            del_sotrudnik2 = head_cols[0].selectbox('**Удаление сотрудника из списка**',names_depart_employes_list(select_depart1), key='leaders2')
            del_sotrudnik_button = head_cols[0].button('Потвердить', on_click=del_sotrudnik, args=[del_sotrudnik2], key='leaders3')    
            
      add_sotrudnik_on = head_cols[0].toggle('**Добавление нового сотрудника**', key='leaders4')
      if add_sotrudnik_on:
            add_sotrudnik_surname = head_cols[0].text_input('**Фамилия** :red["Обязательно!"]')
            add_sotrudnik_name = head_cols[0].text_input('**Имя** :red["Обязательно!"]')
            add_sotrudnik_surname2 = head_cols[0].text_input('**Отчество** :blue["Опционально!"]')
            if add_sotrudnik_surname2 == '':
                  add_sotrudnik2 = add_sotrudnik_surname + ' ' + add_sotrudnik_name
            else:
                  add_sotrudnik2 = add_sotrudnik_surname + ' ' + add_sotrudnik_name + ' ' + add_sotrudnik_surname2
            add_sotrudnik_button = head_cols[0].button('Потвердить', on_click=add_sotrudnik, args=[add_sotrudnik2], key='leaders6', disabled=True if (add_sotrudnik_surname == '' or add_sotrudnik_name == '') else False)
            if add_sotrudnik_button:
                  head_cols[0].write('**Сотрудник добавлен**')
      
with leaders:

      leaders_columns = st.columns(4)
      if select_depart1 not in st.session_state.edfj:
            st.session_state.edfj[select_depart1] = {}
            st.session_state.edij[select_depart1] = {}
      if employee_selection_leaders + '_' + str(select_year) not in st.session_state.edfj[select_depart1]:
            gop_leaders = pd.DataFrame(st.session_state.vcj[str(select_year)])
      else:
            gop_leaders = pd.read_json(st.session_state.edfj[select_depart1][employee_selection_leaders + '_' + str(select_year)])
      def save_file_leaders():
            st.session_state.edfj[select_depart1][employee_selection_leaders + '_' + str(select_year)] = ndf_leaders.to_json(orient='records', force_ascii=False)
            r.json().set('employees_data_frame_yaskovich', '$', st.session_state.edfj)
            st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)] = list_employee_info
            r.json().set('employees_data_info_yaskovich', '$', st.session_state.edij)
      def str_in_int(list):
            for i in range(len(list)):
                  list[i] = int(list[i])
            return list
      
      def time_to_datetime(info):
            info = info.split('-')
            str_in_int(info)
            dateinfo = date(info[0],info[1],info[2])
            return dateinfo
      
      leaders3_columns = st.columns(3)
      leaders3_5_columns = st.columns([2,3,3,2,4,5,2,8,3])
      leaders4_columns = st.columns([2,3,3,2,4,5,2,8,3])
      leaders5_columns = st.columns([2,3,3,2,4,5,2,8,3])
      leaders6_columns = st.columns([2,3,3,2,4,5,2,8,3])
      leaders7_columns = st.columns([2,3,3,2,4,5,2,8,3])
      leaders8_columns = st.columns([2,3,3,2,4,5,2,8,3])
      leaders9_columns = st.columns([2,3,3,2,4,5,2,8,3])
      leaders10_columns= st.columns([2,3,3,2,4,5,2,8,3])


      leaders3_columns[0].success('***Отпуск по плану***')
      leaders3_columns[1].success('***Один отпуск должен >= 14 дням***')
      leaders3_5_columns[0].success('**№**')
      leaders3_5_columns[1].success('**Отпуск от**')  
      leaders3_5_columns[2].success('**Отпуск до**')
      leaders3_5_columns[3].success('**Дни**')
      leaders3_5_columns[4].success('**Отгул/Не отгул**')
      leaders4_columns[0].success('**№1**')
      leaders5_columns[0].success('**№2**')
      leaders6_columns[0].success('**№3**')
      leaders7_columns[0].success('**№4**')
      leaders8_columns[0].success('**№5**')
      leaders9_columns[0].success('**№6**')
      leaders10_columns[0].success('**№7**')
      date_vacation_leaders_min_one = leaders4_columns[1].date_input('От', min_value=date(int(select_year),1,1),max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_one_1", value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][0]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else date(int(select_year),1,1), label_visibility='collapsed')
      date_vacation_leaders_min_two = leaders5_columns[1].date_input('От', min_value=date(int(select_year),1,1),max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_two_1", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][1]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else date(int(select_year),1,1))
      date_vacation_leaders_min_three = leaders6_columns[1].date_input('От', min_value=date(int(select_year),1,1),max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_three_1", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][2]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else date(int(select_year),1,1))
      date_vacation_leaders_min_four = leaders7_columns[1].date_input('От', min_value=date(int(select_year),1,1),max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_four_1", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][3]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else date(int(select_year),1,1))
      date_vacation_leaders_min_five = leaders8_columns[1].date_input('От', min_value=date(int(select_year),1,1),max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_five_1", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][4]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else date(int(select_year),1,1))
      date_vacation_leaders_min_six = leaders9_columns[1].date_input('От', min_value=date(int(select_year),1,1),max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_six_1", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][5]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else date(int(select_year),1,1))
      date_vacation_leaders_min_seven = leaders10_columns[1].date_input('От', min_value=date(int(select_year),1,1),max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_seven_1", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][6]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else date(int(select_year),1,1))
      date_vacation_leaders_max_one = leaders4_columns[2].date_input('До', min_value=date_vacation_leaders_min_one,max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_one_2", value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][7]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][7]) >= date_vacation_leaders_min_one else date_vacation_leaders_min_one, label_visibility='collapsed')
      date_vacation_leaders_max_two = leaders5_columns[2].date_input('До', min_value=date_vacation_leaders_min_two,max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_two_2", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][8]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][8]) >= date_vacation_leaders_min_two else date_vacation_leaders_min_two)
      date_vacation_leaders_max_three = leaders6_columns[2].date_input('До', min_value=date_vacation_leaders_min_three,max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_three_2", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][9]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][9]) >= date_vacation_leaders_min_three else date_vacation_leaders_min_three)
      date_vacation_leaders_max_four = leaders7_columns[2].date_input('До', min_value=date_vacation_leaders_min_four,max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_four_2", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][10]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][10]) >= date_vacation_leaders_min_four else date_vacation_leaders_min_four)
      date_vacation_leaders_max_five = leaders8_columns[2].date_input('До', min_value=date_vacation_leaders_min_five,max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_five_2", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][11]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][11]) >= date_vacation_leaders_min_five else date_vacation_leaders_min_five)
      date_vacation_leaders_max_six = leaders9_columns[2].date_input('До', min_value=date_vacation_leaders_min_six,max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_six_2", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][12]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][12]) >= date_vacation_leaders_min_six else date_vacation_leaders_min_six)
      date_vacation_leaders_max_seven = leaders10_columns[2].date_input('До', min_value=date_vacation_leaders_min_seven,max_value=date(int(select_year),12,31), format='DD/MM/YYYY', key="date_vacation_leaders_seven_2", label_visibility='collapsed', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][13]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][13]) >= date_vacation_leaders_min_seven else date_vacation_leaders_min_seven)
      
      min_value = {0:date_vacation_leaders_min_one,1:date_vacation_leaders_min_two,2:date_vacation_leaders_min_three,3:date_vacation_leaders_min_four,4:date_vacation_leaders_min_five,5:date_vacation_leaders_min_six,6:date_vacation_leaders_min_seven}
      max_value = {0:date_vacation_leaders_max_one,1:date_vacation_leaders_max_two,2:date_vacation_leaders_max_three,3:date_vacation_leaders_max_four,4:date_vacation_leaders_max_five,5:date_vacation_leaders_max_six,6:date_vacation_leaders_max_seven}

      min_date_vacation_leaders_one = int(str(date_vacation_leaders_min_one).split('-')[2])
      min_month_vacation_leaders_one = int(str(date_vacation_leaders_min_one).split('-')[1])

      min_date_vacation_leaders_two = int(str(date_vacation_leaders_min_two).split('-')[2])
      min_month_vacation_leaders_two = int(str(date_vacation_leaders_min_two).split('-')[1])

      min_date_vacation_leaders_three = int(str(date_vacation_leaders_min_three).split('-')[2])
      min_month_vacation_leaders_three = int(str(date_vacation_leaders_min_three).split('-')[1])

      min_date_vacation_leaders_four = int(str(date_vacation_leaders_min_four).split('-')[2])
      min_month_vacation_leaders_four = int(str(date_vacation_leaders_min_four).split('-')[1])

      min_date_vacation_leaders_five = int(str(date_vacation_leaders_min_five).split('-')[2])
      min_month_vacation_leaders_five = int(str(date_vacation_leaders_min_five).split('-')[1])

      min_date_vacation_leaders_six = int(str(date_vacation_leaders_min_six).split('-')[2])
      min_month_vacation_leaders_six = int(str(date_vacation_leaders_min_six).split('-')[1])

      min_date_vacation_leaders_seven = int(str(date_vacation_leaders_min_seven).split('-')[2])
      min_month_vacation_leaders_seven = int(str(date_vacation_leaders_min_seven).split('-')[1])

      max_date_vacation_leaders_one = int(str(date_vacation_leaders_max_one).split('-')[2])
      max_month_vacation_leaders_one = int(str(date_vacation_leaders_max_one).split('-')[1])

      max_date_vacation_leaders_two = int(str(date_vacation_leaders_max_two).split('-')[2])
      max_month_vacation_leaders_two = int(str(date_vacation_leaders_max_two).split('-')[1])

      max_date_vacation_leaders_three = int(str(date_vacation_leaders_max_three).split('-')[2])
      max_month_vacation_leaders_three = int(str(date_vacation_leaders_max_three).split('-')[1])

      max_date_vacation_leaders_four = int(str(date_vacation_leaders_max_four).split('-')[2])
      max_month_vacation_leaders_four = int(str(date_vacation_leaders_max_four).split('-')[1])

      max_date_vacation_leaders_five = int(str(date_vacation_leaders_max_five).split('-')[2])
      max_month_vacation_leaders_five = int(str(date_vacation_leaders_max_five).split('-')[1])

      max_date_vacation_leaders_six = int(str(date_vacation_leaders_max_six).split('-')[2])
      max_month_vacation_leaders_six = int(str(date_vacation_leaders_max_six).split('-')[1])

      max_date_vacation_leaders_seven = int(str(date_vacation_leaders_max_seven).split('-')[2])
      max_month_vacation_leaders_seven = int(str(date_vacation_leaders_max_seven).split('-')[1])
      list_days_first = []
      list_days_second = []

      if min_month_vacation_leaders_one == max_month_vacation_leaders_one:
            number_of_vacation_days_leaders_one = ((max_date_vacation_leaders_one - min_date_vacation_leaders_one + 1) if max_date_vacation_leaders_one != min_date_vacation_leaders_one else 0)
            leaders4_columns[3].success(number_of_vacation_days_leaders_one)
            list_days_first.append(0)
            list_days_second.append(0)
      else:
            number_of_vacation_days_leaders_one = (((int(calendar.monthrange(int(select_year), min_month_vacation_leaders_one)[1]) - min_date_vacation_leaders_one + 1) + int(max_date_vacation_leaders_one)))
            leaders4_columns[3].success(number_of_vacation_days_leaders_one)
            days_in_first_month_one = int(calendar.monthrange(int(select_year), min_month_vacation_leaders_one)[1]) - min_date_vacation_leaders_one + 1
            days_in_second_month_one = max_date_vacation_leaders_one
            list_days_first.append(days_in_first_month_one)
            list_days_second.append(days_in_second_month_one)

      if min_month_vacation_leaders_two == max_month_vacation_leaders_two:
            number_of_vacation_days_leaders_two = ((max_date_vacation_leaders_two - min_date_vacation_leaders_two + 1) if max_date_vacation_leaders_two != min_date_vacation_leaders_two else 0)
            leaders5_columns[3].success(number_of_vacation_days_leaders_two)
            list_days_first.append(0)
            list_days_second.append(0)
      else:
            number_of_vacation_days_leaders_two = (((int(calendar.monthrange(int(select_year), min_month_vacation_leaders_two)[1]) - min_date_vacation_leaders_two + 1) + int(max_date_vacation_leaders_two)))
            leaders5_columns[3].success(number_of_vacation_days_leaders_two)
            days_in_first_month_two = int(calendar.monthrange(int(select_year), min_month_vacation_leaders_two)[1]) - min_date_vacation_leaders_two + 1
            days_in_second_month_two = max_date_vacation_leaders_two
            list_days_first.append(days_in_first_month_two)
            list_days_second.append(days_in_second_month_two)

      if min_month_vacation_leaders_three == max_month_vacation_leaders_three:
            number_of_vacation_days_leaders_three = ((max_date_vacation_leaders_three - min_date_vacation_leaders_three + 1) if max_date_vacation_leaders_three != min_date_vacation_leaders_three else 0)
            leaders6_columns[3].success(number_of_vacation_days_leaders_three)
            list_days_first.append(0)
            list_days_second.append(0)
      else:
            number_of_vacation_days_leaders_three = (((int(calendar.monthrange(int(select_year), min_month_vacation_leaders_three)[1]) - min_date_vacation_leaders_three + 1) + int(max_date_vacation_leaders_three)))
            leaders6_columns[3].success(number_of_vacation_days_leaders_three)
            days_in_first_month_three = int(calendar.monthrange(int(select_year), min_month_vacation_leaders_three)[1]) - min_date_vacation_leaders_three + 1
            days_in_second_month_three = max_date_vacation_leaders_three
            list_days_first.append(days_in_first_month_three)
            list_days_second.append(days_in_second_month_three)

      if min_month_vacation_leaders_four == max_month_vacation_leaders_four:
            number_of_vacation_days_leaders_four = ((max_date_vacation_leaders_four - min_date_vacation_leaders_four + 1) if max_date_vacation_leaders_four != min_date_vacation_leaders_four else 0)
            leaders7_columns[3].success(number_of_vacation_days_leaders_four)
            list_days_first.append(0)
            list_days_second.append(0)
      else:
            number_of_vacation_days_leaders_four = (((int(calendar.monthrange(int(select_year), min_month_vacation_leaders_four)[1]) - min_date_vacation_leaders_four + 1) + int(max_date_vacation_leaders_four)))
            leaders7_columns[3].success(number_of_vacation_days_leaders_four)
            days_in_first_month_four = int(calendar.monthrange(int(select_year), min_month_vacation_leaders_four)[1]) - min_date_vacation_leaders_four + 1
            days_in_second_month_four = max_date_vacation_leaders_four
            list_days_first.append(days_in_first_month_four)
            list_days_second.append(days_in_second_month_four)

      if min_month_vacation_leaders_five == max_month_vacation_leaders_five:
            number_of_vacation_days_leaders_five = ((max_date_vacation_leaders_five - min_date_vacation_leaders_five + 1) if max_date_vacation_leaders_five != min_date_vacation_leaders_five else 0)
            leaders8_columns[3].success(number_of_vacation_days_leaders_five)
            list_days_first.append(0)
            list_days_second.append(0)
      else:
            number_of_vacation_days_leaders_five = (((int(calendar.monthrange(int(select_year), min_month_vacation_leaders_five)[1]) - min_date_vacation_leaders_five + 1) + int(max_date_vacation_leaders_five)))
            leaders8_columns[3].success(number_of_vacation_days_leaders_five)
            days_in_first_month_five = int(calendar.monthrange(int(select_year), min_month_vacation_leaders_five)[1]) - min_date_vacation_leaders_five + 1
            days_in_second_month_five = max_date_vacation_leaders_five
            list_days_first.append(days_in_first_month_five)
            list_days_second.append(days_in_second_month_five)
      
      if min_month_vacation_leaders_six == max_month_vacation_leaders_six:
            number_of_vacation_days_leaders_six = ((max_date_vacation_leaders_six - min_date_vacation_leaders_six + 1) if max_date_vacation_leaders_six != min_date_vacation_leaders_six else 0)
            leaders9_columns[3].success(number_of_vacation_days_leaders_six)
            list_days_first.append(0)
            list_days_second.append(0)
      else:
            number_of_vacation_days_leaders_six = (((int(calendar.monthrange(int(select_year), min_month_vacation_leaders_six)[1]) - min_date_vacation_leaders_six + 1) + int(max_date_vacation_leaders_six)))
            leaders9_columns[3].success(number_of_vacation_days_leaders_six)
            days_in_first_month_six = int(calendar.monthrange(int(select_year), min_month_vacation_leaders_six)[1]) - min_date_vacation_leaders_six + 1
            days_in_second_month_six = max_date_vacation_leaders_six
            list_days_first.append(days_in_first_month_six)
            list_days_second.append(days_in_second_month_six)

      if min_month_vacation_leaders_seven == max_month_vacation_leaders_seven:
            number_of_vacation_days_leaders_seven = ((max_date_vacation_leaders_seven - min_date_vacation_leaders_seven + 1) if max_date_vacation_leaders_seven != min_date_vacation_leaders_seven else 0)
            leaders10_columns[3].success(number_of_vacation_days_leaders_seven)
            list_days_first.append(0)
            list_days_second.append(0)
      else:
            number_of_vacation_days_leaders_seven = (((int(calendar.monthrange(int(select_year), min_month_vacation_leaders_seven)[1]) - min_date_vacation_leaders_seven + 1) + int(max_date_vacation_leaders_seven)))
            leaders10_columns[3].success(number_of_vacation_days_leaders_seven)
            days_in_first_month_seven = int(calendar.monthrange(int(select_year), min_month_vacation_leaders_seven)[1]) - min_date_vacation_leaders_seven + 1
            days_in_second_month_seven = max_date_vacation_leaders_seven
            list_days_first.append(days_in_first_month_seven)
            list_days_second.append(days_in_second_month_seven)


      number_vacation_days = {0:number_of_vacation_days_leaders_one,1:number_of_vacation_days_leaders_two,2:number_of_vacation_days_leaders_three,3:number_of_vacation_days_leaders_four,4:number_of_vacation_days_leaders_five,5:number_of_vacation_days_leaders_six,6:number_of_vacation_days_leaders_seven}

      gop_leaders_clean = pd.DataFrame(st.session_state.vcj[str(select_year)])

      for i in range(31):
            for y in range(12):
                  if gop_leaders[f'{i+1}'][y] == '❎' or gop_leaders[f'{i+1}'][y] == '🟩' or gop_leaders[f'{i+1}'][y] == '🟥':
                        gop_leaders[f'{i+1}'][y] = gop_leaders_clean[f'{i+1}'][y]

      information_table_vacation_leaders2 = leaders3_5_columns[7].success('**Дата трудоустройства**')
      information_table_vacation_leaders3 = leaders4_columns[7].success('**Количество дней отпуска в год**')
      information_table_vacation_leaders4 = leaders5_columns[7].success('**Количество дней отпуска до конца года**')
      
      information_table_vacation_leaders6 = leaders3_5_columns[8].date_input('sad', value=time_to_datetime(st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][21]) if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else date(int(select_year),1,1), label_visibility='collapsed', format='DD/MM/YYYY')
      difference_days = int(str(datetime.strptime(f'{select_year}-12-31', '%Y-%m-%d') - datetime.strptime(str(information_table_vacation_leaders6), '%Y-%m-%d')).split(',')[0].split(' days')[0])
      information_table_vacation_leaders7 = leaders4_columns[8].number_input('Количество дней в год', label_visibility='collapsed', step=1, value=st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][22] if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else 28)
      if calendar.isleap(int(select_year)):
            number_of_vacation_days_until_the_end_of_the_year = round((difference_days+1)/366*information_table_vacation_leaders7,1)
      else:
            number_of_vacation_days_until_the_end_of_the_year = round((difference_days+1)/365*information_table_vacation_leaders7,1)
      if number_of_vacation_days_until_the_end_of_the_year > information_table_vacation_leaders7:
            number_of_vacation_days_until_the_end_of_the_year = 28.0

      information_table_vacation_leaders8 = number_of_vacation_days_until_the_end_of_the_year
      leaders5_columns[8].success(information_table_vacation_leaders8)

      information_table_vacation_leaders9_toggle = leaders4_columns[4].selectbox('Отгулял отпуск №1',['-','Отгулял отпуск №1','Не отгулял отпуск №1'], label_visibility='collapsed', disabled=True if number_of_vacation_days_leaders_one == 0 or number_of_vacation_days_leaders_one == '0' else False, index=st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][14] if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and number_of_vacation_days_leaders_one != 0 else 0)
      information_table_vacation_leaders10_toggle = leaders5_columns[4].selectbox('Отгулял отпуск №2',['-','Отгулял отпуск №2','Не отгулял отпуск №2'], label_visibility='collapsed', disabled=True if number_of_vacation_days_leaders_two == 0 or number_of_vacation_days_leaders_two == '0' else False, index=st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][15] if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and number_of_vacation_days_leaders_two != 0  else 0)
      information_table_vacation_leaders11_toggle = leaders6_columns[4].selectbox('Отгулял отпуск №3',['-','Отгулял отпуск №3','Не отгулял отпуск №3'], label_visibility='collapsed', disabled=True if number_of_vacation_days_leaders_three == 0 or number_of_vacation_days_leaders_three == '0' else False, index=st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][16] if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and number_of_vacation_days_leaders_three != 0  else 0)
      information_table_vacation_leaders12_toggle = leaders7_columns[4].selectbox('Отгулял отпуск №4',['-','Отгулял отпуск №4','Не отгулял отпуск №4'], label_visibility='collapsed', disabled=True if number_of_vacation_days_leaders_four == 0 or number_of_vacation_days_leaders_four == '0' else False, index=st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][17] if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and number_of_vacation_days_leaders_four != 0  else 0)
      information_table_vacation_leaders13_toggle = leaders8_columns[4].selectbox('Отгулял отпуск №5',['-','Отгулял отпуск №5','Не отгулял отпуск №5'], label_visibility='collapsed', disabled=True if number_of_vacation_days_leaders_five == 0 or number_of_vacation_days_leaders_five == '0' else False, index=st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][18] if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and number_of_vacation_days_leaders_five != 0  else 0)
      information_table_vacation_leaders14_toggle = leaders9_columns[4].selectbox('Отгулял отпуск №6',['-','Отгулял отпуск №6','Не отгулял отпуск №6'], label_visibility='collapsed', disabled=True if number_of_vacation_days_leaders_six == 0 or number_of_vacation_days_leaders_six == '0' else False, index=st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][19] if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and number_of_vacation_days_leaders_six != 0  else 0)
      information_table_vacation_leaders15_toggle = leaders10_columns[4].selectbox('Отгулял отпуск №7',['-','Отгулял отпуск №7','Не отгулял отпуск №7'], label_visibility='collapsed', disabled=True if number_of_vacation_days_leaders_seven == 0 or number_of_vacation_days_leaders_seven == '0' else False, index=st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][20] if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] and number_of_vacation_days_leaders_seven != 0  else 0)


      dict_index_toggle = {
            '-':0,
            'Отгулял отпуск №1':1,
            'Не отгулял отпуск №1':2,
            'Отгулял отпуск №2':1,
            'Не отгулял отпуск №2':2,
            'Отгулял отпуск №3':1,
            'Не отгулял отпуск №3':2,
            'Отгулял отпуск №4':1,
            'Не отгулял отпуск №4':2,
            'Отгулял отпуск №5':1,
            'Не отгулял отпуск №5':2,
            'Отгулял отпуск №6':1,
            'Не отгулял отпуск №6':2,
            'Отгулял отпуск №7':1,
            'Не отгулял отпуск №7':2,
      }
      
      toggle_on_off_list = []

      if information_table_vacation_leaders9_toggle == 'Отгулял отпуск №1':
            toggle_on_off_list.append(1)
      elif information_table_vacation_leaders9_toggle == 'Не отгулял отпуск №1':
            toggle_on_off_list.append(2)
      else:
            toggle_on_off_list.append(0)
      if information_table_vacation_leaders10_toggle== 'Отгулял отпуск №2':
            toggle_on_off_list.append(1)
      elif information_table_vacation_leaders10_toggle == 'Не отгулял отпуск №2':
            toggle_on_off_list.append(2)
      else:
            toggle_on_off_list.append(0)
      if information_table_vacation_leaders11_toggle== 'Отгулял отпуск №3':
            toggle_on_off_list.append(1)
      elif information_table_vacation_leaders11_toggle == 'Не отгулял отпуск №3':
            toggle_on_off_list.append(2)
      else:
            toggle_on_off_list.append(0)
      if information_table_vacation_leaders12_toggle== 'Отгулял отпуск №4':
            toggle_on_off_list.append(1)
      elif information_table_vacation_leaders12_toggle == 'Не отгулял отпуск №4':
            toggle_on_off_list.append(2)
      else:
            toggle_on_off_list.append(0)
      if information_table_vacation_leaders13_toggle== 'Отгулял отпуск №5':
            toggle_on_off_list.append(1)
      elif information_table_vacation_leaders13_toggle == 'Не отгулял отпуск №5':
            toggle_on_off_list.append(2)
      else:
            toggle_on_off_list.append(0)
      if information_table_vacation_leaders14_toggle== 'Отгулял отпуск №6':
            toggle_on_off_list.append(1)
      elif information_table_vacation_leaders14_toggle == 'Не отгулял отпуск №6':
            toggle_on_off_list.append(2)
      else:
            toggle_on_off_list.append(0)
      if information_table_vacation_leaders15_toggle== 'Отгулял отпуск №7':
            toggle_on_off_list.append(1)
      elif information_table_vacation_leaders15_toggle == 'Не отгулял отпуск №7':
            toggle_on_off_list.append(2)
      else:
            toggle_on_off_list.append(0)


      for i in range(7):
            min_value_date = min_value[i]
            min_value_date = str(min_value_date)
            min_value_date = min_value_date[:10].split('-')
            min_value_date = str_in_int(min_value_date)
            max_value_date = max_value[i]
            max_value_date = str(max_value_date)
            max_value_date = max_value_date[:10].split('-')
            max_value_date = str_in_int(max_value_date)
            days_value_date = number_vacation_days[i]
            if min_value_date[1] == max_value_date[1]:
                  for y in range(int(days_value_date)):
                        if gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1]-1] == '▪️' or gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1]-1] == '⬜':
                              if toggle_on_off_list[i] == 2:
                                    gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1]-1] = '🟥'
                              elif toggle_on_off_list[i] == 1:
                                    gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1]-1] = '🟩'
                              else:
                                    gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1]-1] = '❎'
            elif min_value_date[1] != max_value_date[1]:
                        for y in range(int(list_days_first[i])):
                              if gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1]-1] == '▪️' or gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1] -1] == '⬜':
                                    if toggle_on_off_list[i] == 2:
                                          gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1]-1] = '🟥'
                                    elif toggle_on_off_list[i] == 1:
                                          gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1]-1] = '🟩'
                                    else:
                                          gop_leaders[f'{int(min_value_date[2]+y)}'][min_value_date[1]-1] = '❎'
                        for j in range(int(list_days_second[i])):
                              if gop_leaders[f'{j+1}'][max_value_date[1]-1] == '▪️' or gop_leaders[f'{j+1}'][max_value_date[1] -1] == '⬜':
                                    if toggle_on_off_list[i] == 2:
                                          gop_leaders[f'{j+1}'][max_value_date[1]-1] = '🟥'
                                    elif toggle_on_off_list[i] == 1:
                                          gop_leaders[f'{j+1}'][max_value_date[1]-1] = '🟩'
                                    else:
                                          gop_leaders[f'{j+1}'][max_value_date[1]-1] = '❎'
      information_table_vacation_leaders1 = leaders6_columns[7].success('**Количество дней отпуска с прошлого года**')
      information_table_vacation_leaders5 = leaders6_columns[8].number_input('Количество дней', value=st.session_state.edij[select_depart1][employee_selection_leaders + '_' + str(select_year)][23] if employee_selection_leaders + '_' + str(select_year) in st.session_state.edij[select_depart1] else 0, label_visibility='collapsed', step=1)

      information_table_vacation_leaders9 = leaders3_5_columns[5].success('**По плану ушёл в отпуск**')
      information_table_vacation_leaders10 = leaders4_columns[5].success('**По плану в отд. кадров**')
      information_table_vacation_leaders11 = leaders5_columns[5].success('**Отпуск**')
      information_table_vacation_leaders12 = leaders6_columns[5].success('**Отпуск не официально**')
      information_table_vacation_leaders13 = leaders7_columns[5].success('**Отпуск за свой счёт**')
      information_table_vacation_leaders14 = leaders8_columns[5].success('**Не ушел на заплан. отп.**')

      information_table_vacation_leaders15 = leaders9_columns[5].success('**Перенос с**')
      information_table_vacation_leaders16 = leaders10_columns[5].success('**Перенесен на**')
      information_table_vacation_leaders20 = leaders7_columns[7].success('**Перенос, не отход.**')
      information_table_vacation_leaders17 = leaders8_columns[7].success('**Не согласовано**')
      information_table_vacation_leaders18 = leaders9_columns[7].success('**Осталось дней по факту**')
      information_table_vacation_leaders19 = leaders10_columns[7].success('**Осталось дней официально**')

      

      leaders11_columns = st.columns(4)
      leaders11_columns[0].button('Сохранить изменения', on_click=save_file_leaders, use_container_width=True)

      legends_info = leaders11_columns[1].toggle('Показать условные знаки/легенду календаря')
      if legends_info:
            legends_leaders = st.columns(5)
            legends_leaders[4].write(emoji.emojize(':black_large_square:') + ' Отсутсвующие дни в месяце')
            legends_leaders[4].write(emoji.emojize(':black_small_square:') + ' Выходные/Праздники')
            legends_leaders[2].write(emoji.emojize(':black_square_button:') + ' Отпуск не официально')
            legends_leaders[1].write(emoji.emojize(':blue_square:') + ' Отпуск перенесен с...')
            legends_leaders[2].write(emoji.emojize(':brown_square:') + ' Отпуск за свой счёт')
            legends_leaders[0].write(emoji.emojize(':cross_mark_button:')  + ' По плану отпуск в Отделе Кадров')
            legends_leaders[0].write(emoji.emojize(':green_square:') + ' По плану ушел в Отпуск')
            legends_leaders[2].write(emoji.emojize(':orange_square:') + ' Не согласовано')
            legends_leaders[1].write(emoji.emojize(':stop_button:') + ' Отпуск перенесён на...')
            legends_leaders[0].write(emoji.emojize(':red_square:') + ' Не ушёл в запланированый отпуск')
            legends_leaders[1].write(emoji.emojize(':FREE_button:') + ' Отпуск')
            legends_leaders[3].write(emoji.emojize(':white_square_button:') + ' Перенос, не отходил')
            legends_leaders[4].write(emoji.emojize(':white_large_square:') + ' Рабочий день')

      ndf_leaders = st.data_editor(
            gop_leaders,
            column_config={
                  'Месяц': st.column_config.SelectboxColumn( 
                        'Месяц',
                        width=70,
                        required=False,
                  ),
                  '1': st.column_config.SelectboxColumn( 
                        '1',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '2': st.column_config.SelectboxColumn(
                        '2',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '3': st.column_config.SelectboxColumn(
                        '3',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '4': st.column_config.SelectboxColumn(
                        '4',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '5': st.column_config.SelectboxColumn(
                        '5',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '6': st.column_config.SelectboxColumn(
                        '6',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '7': st.column_config.SelectboxColumn(
                        '7',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '8': st.column_config.SelectboxColumn(
                        '8',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '9': st.column_config.SelectboxColumn(
                        '9',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '10': st.column_config.SelectboxColumn(
                        '10',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '11': st.column_config.SelectboxColumn(
                        '11',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '12': st.column_config.SelectboxColumn(
                        '12',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '13': st.column_config.SelectboxColumn(
                        '13',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '14': st.column_config.SelectboxColumn(
                        '14',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '15': st.column_config.SelectboxColumn(
                        '15',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '16': st.column_config.SelectboxColumn(
                        '16',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '17': st.column_config.SelectboxColumn(
                        '17',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '18': st.column_config.SelectboxColumn(
                        '18',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '19': st.column_config.SelectboxColumn(
                        '19',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '20': st.column_config.SelectboxColumn(
                        '20',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '21': st.column_config.SelectboxColumn(
                        '21',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '22': st.column_config.SelectboxColumn(
                        '22',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '23': st.column_config.SelectboxColumn(
                        '23',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '24': st.column_config.SelectboxColumn(
                        '24',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '25': st.column_config.SelectboxColumn(
                        '25',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '26': st.column_config.SelectboxColumn(
                        '26',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '27': st.column_config.SelectboxColumn(
                        '27',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '28': st.column_config.SelectboxColumn(
                        '28',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '29': st.column_config.SelectboxColumn(
                        '29',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '30': st.column_config.SelectboxColumn(
                        '30',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                        
                        required=False,
                  ),
                  '31': st.column_config.SelectboxColumn(
                        '31',
                        width=45,
                        options=[
                              emoji.emojize(':white_large_square:'),
                              emoji.emojize(':black_square_button:'),
                              emoji.emojize(':blue_square:'),
                              emoji.emojize(':brown_square:'),
                              emoji.emojize(':orange_square:'),
                              emoji.emojize(':stop_button:'),
                              emoji.emojize(':FREE_button:'),
                              emoji.emojize(':white_square_button:'),
                              emoji.emojize(':black_small_square:')
                        ],
                  
                        required=False,
                  )
                  
            },
            hide_index=True,
            width=1650,
            height=465
            )  

      if 'select_month1' not in st.session_state:
            st.session_state.select_month1 = 'Январь'

      went_on_vacation_as_planned                      = 0
      according_to_the_plan_leave_in_the_hr_department = 0
      vacation                                         = 0
      vacation_is_not_official                         = 0
      vacation_at_your_own_expense                     = 0
      didnt_go_on_a_planned_vacation                   = 0
      transfer_s                                       = 0
      moved_to                                         = 0
      transfer_not_departure                           = 0
      not_agreed                                       = 0
      days_remaining_actually                          = 0
      officially_days_left                             = 0

      for i in range(31):
            for y in range(12):
                  if ndf_leaders[str(i+1)][y] == '🟩':
                        went_on_vacation_as_planned = went_on_vacation_as_planned + 1
                  if ndf_leaders[str(i+1)][y] == '❎':
                        according_to_the_plan_leave_in_the_hr_department = according_to_the_plan_leave_in_the_hr_department + 1
                  if ndf_leaders[str(i+1)][y] == '🆓':
                        vacation = vacation + 1
                  if ndf_leaders[str(i+1)][y] == '🔲':
                        vacation_is_not_official = vacation_is_not_official + 1
                  if ndf_leaders[str(i+1)][y] == '🟫':
                        vacation_at_your_own_expense = vacation_at_your_own_expense + 1
                  if ndf_leaders[str(i+1)][y] == '🟥':
                        didnt_go_on_a_planned_vacation = didnt_go_on_a_planned_vacation + 1
                  if ndf_leaders[str(i+1)][y] == '🟦':
                        transfer_s = transfer_s + 1
                  if ndf_leaders[str(i+1)][y] == '⏹️':
                        moved_to = moved_to + 1
                  if ndf_leaders[str(i+1)][y] == '🔳':
                        transfer_not_departure = transfer_not_departure + 1
                  if ndf_leaders[str(i+1)][y] == '🟧':
                        not_agreed = not_agreed + 1

      officially_days_left = int(information_table_vacation_leaders8) - according_to_the_plan_leave_in_the_hr_department - went_on_vacation_as_planned - vacation + not_agreed - didnt_go_on_a_planned_vacation - transfer_not_departure - moved_to

      days_remaining_actually = int(information_table_vacation_leaders8) + information_table_vacation_leaders5 - went_on_vacation_as_planned - according_to_the_plan_leave_in_the_hr_department - vacation - not_agreed - vacation_is_not_official - moved_to

      leaders3_5_columns[6].success(went_on_vacation_as_planned)
      leaders4_columns[6].success(according_to_the_plan_leave_in_the_hr_department)
      leaders5_columns[6].success(vacation)
      leaders6_columns[6].success(vacation_is_not_official)
      leaders7_columns[6].success(vacation_at_your_own_expense)
      leaders8_columns[6].success(didnt_go_on_a_planned_vacation)
      leaders9_columns[6].success(transfer_s)
      leaders10_columns[6].success(moved_to)
      leaders7_columns[8].success(transfer_not_departure)
      leaders8_columns[8].success(not_agreed)
      leaders9_columns[8].success(days_remaining_actually)
      leaders10_columns[8].success(officially_days_left)
      list_employee_info = [str(date_vacation_leaders_min_one),str(date_vacation_leaders_min_two),str(date_vacation_leaders_min_three),str(date_vacation_leaders_min_four),str(date_vacation_leaders_min_five),str(date_vacation_leaders_min_six),str(date_vacation_leaders_min_seven),str(date_vacation_leaders_max_one),str(date_vacation_leaders_max_two),str(date_vacation_leaders_max_three),str(date_vacation_leaders_max_four),str(date_vacation_leaders_max_five),str(date_vacation_leaders_max_six),str(date_vacation_leaders_max_seven),dict_index_toggle[information_table_vacation_leaders9_toggle],dict_index_toggle[information_table_vacation_leaders10_toggle],dict_index_toggle[information_table_vacation_leaders11_toggle],dict_index_toggle[information_table_vacation_leaders12_toggle],dict_index_toggle[information_table_vacation_leaders13_toggle],dict_index_toggle[information_table_vacation_leaders14_toggle],dict_index_toggle[information_table_vacation_leaders15_toggle],str(information_table_vacation_leaders6),information_table_vacation_leaders7,information_table_vacation_leaders5]
with calendar2:
      
      first_week = {}
      first_week_date = {}
      second_week = {}
      second_week_date = {}
      third_week = {}
      third_week_date = {}
      fourth_week = {}
      fourth_week_date = {}
      fifth_week = {}
      fifth_week_date = {}
      sixth_week = {}
      sixth_week_date = {}
      head_cols2 = st.columns(6)
      st.session_state.select_month1 = head_cols2[0].selectbox('Месяц', date_month_list, key='sm1')
      df = (df_month_year(int(select_year), date_month_nomer[st.session_state.select_month1]))
      for i in range(len(df[0])):
            if df[0][i] == '1' and i == 0:
                  first_week.setdefault('Понедельник','')
            elif df[0][i] == '1' and i == 1:
                  first_week.setdefault('Вторник','')
            elif df[0][i] == '1' and i == 2:
                  first_week.setdefault('Среда','') 
            elif df[0][i] == '1' and i == 3:
                  first_week.setdefault('Четверг','') 
            elif df[0][i] == '1' and i == 4:
                  first_week.setdefault('Пятница','') 
            elif df[0][i] == '1' and i == 5:
                  first_week.setdefault('Суббота','') 
            else:
                  first_week.update(df[0][i])
                  first_week_date.update(df[0][i])
      first_week_df = []
      first_week_df.append(first_week)
      for i in range(len(df[1])):
            if df[1][i] == '1' and i == 0:
                  second_week.setdefault('Понедельник','')
            elif df[1][i] == '1' and i == 1:
                  second_week.setdefault('Вторник','')
            elif df[1][i] == '1' and i == 2:
                  second_week.setdefault('Среда','') 
            elif df[1][i] == '1' and i == 3:
                  second_week.setdefault('Четверг','') 
            elif df[1][i] == '1' and i == 4:
                  second_week.setdefault('Пятница','') 
            elif df[1][i] == '1' and i == 5:
                  second_week.setdefault('Суббота','') 
            else:
                  second_week.update(df[1][i])
                  second_week_date.update(df[1][i])
      second_week_df = []
      second_week_df.append(second_week)
      for i in range(len(df[2])):
            if df[2][i] == '1' and i == 0:
                  third_week.setdefault('Понедельник','')
            elif df[2][i] == '1' and i == 1:
                  third_week.setdefault('Вторник','')
            elif df[2][i] == '1' and i == 2:
                  third_week.setdefault('Среда','') 
            elif df[2][i] == '1' and i == 3:
                  third_week.setdefault('Четверг','') 
            elif df[2][i] == '1' and i == 4:
                  third_week.setdefault('Пятница','') 
            elif df[2][i] == '1' and i == 5:
                  third_week.setdefault('Суббота','') 
            else:
                  third_week.update(df[2][i])
                  third_week_date.update(df[2][i])
      third_week_df = []
      third_week_df.append(third_week)
      for i in range(len(df[3])):
            if df[3][i] == '1' and i == 0:
                  fourth_week.setdefault('Понедельник','')
            elif df[3][i] == '1' and i == 1:
                  fourth_week.setdefault('Вторник','')
            elif df[3][i] == '1' and i == 2:
                  fourth_week.setdefault('Среда','') 
            elif df[3][i] == '1' and i == 3:
                  fourth_week.setdefault('Четверг','') 
            elif df[3][i] == '1' and i == 4:
                  fourth_week.setdefault('Пятница','') 
            elif df[3][i] == '1' and i == 5:
                  fourth_week.setdefault('Суббота','') 
            else:
                  fourth_week.update(df[3][i])
                  fourth_week_date.update(df[3][i])
      fourth_week_df = []
      fourth_week_df.append(fourth_week)
      try:
            for i in range(len(df[4])):
                  if df[4][i] == '1' and i == 0:
                        fifth_week.setdefault('Понедельник','')
                  elif df[4][i] == '1' and i == 1:
                        fifth_week.setdefault('Вторник','')
                  elif df[4][i] == '1' and i == 2:
                        fifth_week.setdefault('Среда','') 
                  elif df[4][i] == '1' and i == 3:
                        fifth_week.setdefault('Четверг','') 
                  elif df[4][i] == '1' and i == 4:
                        fifth_week.setdefault('Пятница','') 
                  elif df[4][i] == '1' and i == 5:
                        fifth_week.setdefault('Суббота','')
                  elif df[4][i] == '1' and i == 6:
                        fifth_week.setdefault('Воскресенье','')
                  else:
                        fifth_week.update(df[4][i])
                        fifth_week_date.update(df[4][i])
            fifth_week_df = []
            fifth_week_df.append(fifth_week)
      except:
            pass
      try:
            for i in range(len(df[5])):
                  if df[5][i] == '1' and i == 0:
                        sixth_week.setdefault('Понедельник','')
                  elif df[5][i] == '1' and i == 1:
                        sixth_week.setdefault('Вторник','')
                  elif df[5][i] == '1' and i == 2:
                        sixth_week.setdefault('Среда','') 
                  elif df[5][i] == '1' and i == 3:
                        sixth_week.setdefault('Четверг','') 
                  elif df[5][i] == '1' and i == 4:
                        sixth_week.setdefault('Пятница','') 
                  elif df[5][i] == '1' and i == 5:
                        sixth_week.setdefault('Суббота','')
                  elif df[5][i] == '1' and i == 6:
                        sixth_week.setdefault('Воскресенье','')
                  else:
                        sixth_week.update(df[5][i])
                        sixth_week_date.update(df[5][i])
            sixth_week_df = []
            sixth_week_df.append(sixth_week)
      except:
            pass
      
      counting = {}

      dict_info_employee_clean = st.session_state.vcj[str(select_year)]
      for y in names_depart_employes_list(select_depart1):
            try:
                  dict_info_employee = pd.read_json(st.session_state.edfj[select_depart1][y + '_' + str(select_year)])
            except:
                  dict_info_employee = st.session_state.vcj[str(select_year)]
            for i in range(calendar.monthrange(int(select_year), date_month_nomer[st.session_state.select_month1])[1]):
                  if dict_info_employee[str(i+1)][date_month_nomer[st.session_state.select_month1]-1] == '🟥' and dict_info_employee_clean[str(i+1)][date_month_nomer[st.session_state.select_month1]-1] != '▪️' or dict_info_employee[str(i+1)][date_month_nomer[st.session_state.select_month1]-1] == '🟦' and dict_info_employee_clean[str(i+1)][date_month_nomer[st.session_state.select_month1]-1] != '▪️' or dict_info_employee[str(i+1)][date_month_nomer[st.session_state.select_month1]-1] == '🔳' and dict_info_employee_clean[str(i+1)][date_month_nomer[st.session_state.select_month1]-1] != '▪️' or dict_info_employee[str(i+1)][date_month_nomer[st.session_state.select_month1]-1] == '⬜' and dict_info_employee_clean[str(i+1)][date_month_nomer[st.session_state.select_month1]-1] != '▪️':
                              if len(str(i)) == 1 and i != 9:
                                    if '0'+str(i+1) in counting.keys():
                                          counting['0'+str(i+1)] = counting['0'+str(i+1)] + 1
                                    else:
                                          counting['0'+str(i+1)] = 1
                              else:
                                    if str(i+1) in counting.keys():
                                          counting[str(i+1)] = counting[str(i+1)] + 1
                                    else:
                                          counting[str(i+1)] = 1
                  else:
                              if len(str(i)) == 1 and i != 9:
                                    if '0'+str(i+1) in counting.keys():
                                          continue
                                    else:
                                          counting['0'+str(i+1)] = 0
                              else:
                                    if str(i+1) in counting.keys():
                                          continue
                                    else:
                                          counting[str(i+1)] = 0
                          
      if first_week_df[0]['Понедельник'] != '':
            first_week_df[0]['Понедельник'] = int(counting[str(first_week_date['Понедельник'])])
            first_week_df[0]['Вторник'] = int(counting[str(first_week_date['Вторник'])])
            first_week_df[0]['Среда'] = int(counting[str(first_week_date['Среда'])])
            first_week_df[0]['Четверг'] = int(counting[str(first_week_date['Четверг'])])
            first_week_df[0]['Пятница'] = int(counting[str(first_week_date['Пятница'])])
            first_week_df[0]['Суббота'] = int(counting[str(first_week_date['Суббота'])])
            first_week_df[0]['Воскресенье'] = int(counting[str(first_week_date['Воскресенье'])])
            st.dataframe(
                  first_week_df,
                  column_config={
                        'Понедельник': st.column_config.ProgressColumn(
                              str(first_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Понедельник']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Вторник': st.column_config.ProgressColumn(
                              str(first_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Вторник']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Среда': st.column_config.ProgressColumn(
                              str(first_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else (st.session_state.select_month1   [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Среда']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Четверг': st.column_config.ProgressColumn(
                              str(first_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Четверг']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Пятница': st.column_config.ProgressColumn(
                              str(first_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Пятница']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Суббота': st.column_config.ProgressColumn(
                              str(first_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Суббота']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(first_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ' )+ 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )
      elif first_week_df[0]['Вторник'] != '':
            first_week_df[0]['Вторник'] = int(counting[str(first_week_date['Вторник'])])
            first_week_df[0]['Среда'] = int(counting[str(first_week_date['Среда'])])
            first_week_df[0]['Четверг'] = int(counting[str(first_week_date['Четверг'])])
            first_week_df[0]['Пятница'] = int(counting[str(first_week_date['Пятница'])])
            first_week_df[0]['Суббота'] = int(counting[str(first_week_date['Суббота'])])
            first_week_df[0]['Воскресенье'] = int(counting[str(first_week_date['Воскресенье'])])
            st.dataframe(
                  first_week_df,
                  column_config={
                        'Понедельник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Вторник': st.column_config.ProgressColumn(
                              str(first_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Вторник']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Среда': st.column_config.ProgressColumn(
                              str(first_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else (st.session_state.select_month1   [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Среда']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Четверг': st.column_config.ProgressColumn(
                              str(first_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Четверг']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Пятница': st.column_config.ProgressColumn(
                              str(first_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Пятница']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Суббота': st.column_config.ProgressColumn(
                              str(first_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Суббота']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(first_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ' )+ 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )
      elif first_week_df[0]['Среда'] != '':
            first_week_df[0]['Среда'] = int(counting[str(first_week_date['Среда'])])
            first_week_df[0]['Четверг'] = int(counting[str(first_week_date['Четверг'])])
            first_week_df[0]['Пятница'] = int(counting[str(first_week_date['Пятница'])])
            first_week_df[0]['Суббота'] = int(counting[str(first_week_date['Суббота'])])
            first_week_df[0]['Воскресенье'] = int(counting[str(first_week_date['Воскресенье'])])
            st.dataframe(
                  first_week_df,
                  column_config={
                        'Понедельник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Вторник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Среда': st.column_config.ProgressColumn(
                              str(first_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else (st.session_state.select_month1   [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Среда']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Четверг': st.column_config.ProgressColumn(
                              str(first_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Четверг']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Пятница': st.column_config.ProgressColumn(
                              str(first_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Пятница']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Суббота': st.column_config.ProgressColumn(
                              str(first_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Суббота']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(first_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )
      elif first_week_df[0]['Четверг'] != '':
            first_week_df[0]['Четверг'] = int(counting[str(first_week_date['Четверг'])])
            first_week_df[0]['Пятница'] = int(counting[str(first_week_date['Пятница'])])
            first_week_df[0]['Суббота'] = int(counting[str(first_week_date['Суббота'])])
            first_week_df[0]['Воскресенье'] = int(counting[str(first_week_date['Воскресенье'])])
            st.dataframe(
                  first_week_df,
                  column_config={
                        'Понедельник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Вторник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Среда': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Четверг': st.column_config.ProgressColumn(
                              str(first_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Четверг']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Пятница': st.column_config.ProgressColumn(
                              str(first_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Пятница']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Суббота': st.column_config.ProgressColumn(
                              str(first_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Суббота']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(first_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ' )+ 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )
      elif first_week_df[0]['Пятница'] != '':
            first_week_df[0]['Пятница'] = int(counting[str(first_week_date['Пятница'])])
            first_week_df[0]['Суббота'] = int(counting[str(first_week_date['Суббота'])])
            first_week_df[0]['Воскресенье'] = int(counting[str(first_week_date['Воскресенье'])])
            st.dataframe(
                  first_week_df,
                  column_config={
                        'Понедельник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Вторник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Среда': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Четверг': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Пятница': st.column_config.ProgressColumn(
                              str(first_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Пятница']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Суббота': st.column_config.ProgressColumn(
                              str(first_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Суббота']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(first_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ' )+ 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )
      elif first_week_df[0]['Суббота'] != '':
            first_week_df[0]['Суббота'] = int(counting[str(first_week_date['Суббота'])])
            first_week_df[0]['Воскресенье'] = int(counting[str(first_week_date['Воскресенье'])])
            st.dataframe(
                  first_week_df,
                  column_config={
                        'Понедельник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Вторник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Среда': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Четверг': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Пятница': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Суббота': st.column_config.ProgressColumn(
                              str(first_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Суббота']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(first_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ' )+ 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )
      elif first_week_df[0]['Воскресенье'] != '':
            first_week_df[0]['Воскресенье'] = int(counting[str(first_week_date['Воскресенье'])])
            st.dataframe(
                  first_week_df,
                  column_config={
                        'Понедельник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Вторник': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Среда': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Четверг': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Пятница': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Суббота': st.column_config.Column(
                              '',
                              width='medium',
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(first_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ' )+ 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(first_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )

      if second_week_df[0]['Понедельник'] != '':
            second_week_df[0]['Понедельник'] = int(counting[str(second_week_date['Понедельник'])])
            second_week_df[0]['Вторник'] = int(counting[str(second_week_date['Вторник'])])
            second_week_df[0]['Среда'] = int(counting[str(second_week_date['Среда'])])
            second_week_df[0]['Четверг'] = int(counting[str(second_week_date['Четверг'])])
            second_week_df[0]['Пятница'] = int(counting[str(second_week_date['Пятница'])])
            second_week_df[0]['Суббота'] = int(counting[str(second_week_date['Суббота'])])
            second_week_df[0]['Воскресенье'] = int(counting[str(second_week_date['Воскресенье'])])
            st.dataframe(
                  second_week_df,
                  column_config={
                        'Понедельник': st.column_config.ProgressColumn(
                              str(second_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else     (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                              width='medium',
                              format= '%d %s %d' % (int(second_week_df[0]['Понедельник']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Вторник': st.column_config.ProgressColumn(
                              str(second_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else   (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                              width='medium',
                              format= '%d %s %d' % (int(second_week_df[0]['Вторник']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Среда': st.column_config.ProgressColumn(
                              str(second_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else (st.session_state.select_month1  [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                              width='medium',
                              format= '%d %s %d' % (int(second_week_df[0]['Среда']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Четверг': st.column_config.ProgressColumn(
                              str(second_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else   (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                              width='medium',
                              format= '%d %s %d' % (int(second_week_df[0]['Четверг']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Пятница': st.column_config.ProgressColumn(
                              str(second_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else   (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                              width='medium',
                              format= '%d %s %d' % (int(second_week_df[0]['Пятница']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Суббота': st.column_config.ProgressColumn(
                              str(second_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else   (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                              width='medium',
                              format= '%d %s %d' % (int(second_week_df[0]['Суббота']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(second_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else     (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ' )+ 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(second_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )
      if third_week_df[0]['Понедельник'] != '':
            third_week_df[0]['Понедельник'] = int(counting[str(third_week_date['Понедельник'])])
            third_week_df[0]['Вторник'] = int(counting[str(third_week_date['Вторник'])])
            third_week_df[0]['Среда'] = int(counting[str(third_week_date['Среда'])])
            third_week_df[0]['Четверг'] = int(counting[str(third_week_date['Четверг'])])
            third_week_df[0]['Пятница'] = int(counting[str(third_week_date['Пятница'])])
            third_week_df[0]['Суббота'] = int(counting[str(third_week_date['Суббота'])])
            third_week_df[0]['Воскресенье'] = int(counting[str(third_week_date['Воскресенье'])])
            st.dataframe(
                  third_week_df,
                  column_config={
                        'Понедельник': st.column_config.ProgressColumn(
                              str(third_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                              width='medium',
                              format= '%d %s %d' % (int(third_week_df[0]['Понедельник']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Вторник': st.column_config.ProgressColumn(
                              str(third_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                              width='medium',
                              format= '%d %s %d' % (int(third_week_df[0]['Вторник']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Среда': st.column_config.ProgressColumn(
                              str(third_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else (st.session_state.select_month1   [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                              width='medium',
                              format= '%d %s %d' % (int(third_week_df[0]['Среда']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Четверг': st.column_config.ProgressColumn(
                              str(third_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                              width='medium',
                              format= '%d %s %d' % (int(third_week_df[0]['Четверг']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Пятница': st.column_config.ProgressColumn(
                              str(third_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                              width='medium',
                              format= '%d %s %d' % (int(third_week_df[0]['Пятница']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Суббота': st.column_config.ProgressColumn(
                              str(third_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                              width='medium',
                              format= '%d %s %d' % (int(third_week_df[0]['Суббота']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(third_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(third_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )
      if fourth_week_df[0]['Понедельник'] != '':
            fourth_week_df[0]['Понедельник'] = int(counting[str(fourth_week_date['Понедельник'])])
            fourth_week_df[0]['Вторник'] = int(counting[str(fourth_week_date['Вторник'])])
            fourth_week_df[0]['Среда'] = int(counting[str(fourth_week_date['Среда'])])
            fourth_week_df[0]['Четверг'] = int(counting[str(fourth_week_date['Четверг'])])
            fourth_week_df[0]['Пятница'] = int(counting[str(fourth_week_date['Пятница'])])
            fourth_week_df[0]['Суббота'] = int(counting[str(fourth_week_date['Суббота'])])
            fourth_week_df[0]['Воскресенье'] = int(counting[str(fourth_week_date['Воскресенье'])])
            st.dataframe(
                  fourth_week_df,
                  column_config={
                        'Понедельник': st.column_config.ProgressColumn(
                              str(fourth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else     (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                              width='medium',
                              format= '%d %s %d' % (int(fourth_week_df[0]['Понедельник']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Вторник': st.column_config.ProgressColumn(
                              str(fourth_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else   (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                              width='medium',
                              format= '%d %s %d' % (int(fourth_week_df[0]['Вторник']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Среда': st.column_config.ProgressColumn(
                              str(fourth_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else (st.session_state.select_month1  [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                              width='medium',
                              format= '%d %s %d' % (int(fourth_week_df[0]['Среда']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Четверг': st.column_config.ProgressColumn(
                              str(fourth_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else   (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                              width='medium',
                              format= '%d %s %d' % (int(fourth_week_df[0]['Четверг']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Пятница': st.column_config.ProgressColumn(
                              str(fourth_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else   (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                              width='medium',
                              format= '%d %s %d' % (int(fourth_week_df[0]['Пятница']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Суббота': st.column_config.ProgressColumn(
                              str(fourth_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else   (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                              width='medium',
                              format= '%d %s %d' % (int(fourth_week_df[0]['Суббота']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                        'Воскресенье': st.column_config.ProgressColumn(
                              str(fourth_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else     (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Воскресенье',
                              width='medium',
                              format= '%d %s %d' % (int(fourth_week_df[0]['Воскресенье']), 'из', max_worker ),
                              min_value=0,
                              max_value=max_worker,
                        ),
                  },
            )

      try:
            if fifth_week_df[0]['Воскресенье'] != '':
                  fifth_week_df[0]['Понедельник'] = int(counting[str(fifth_week_date['Понедельник'])])
                  fifth_week_df[0]['Вторник'] = int(counting[str(fifth_week_date['Вторник'])])
                  fifth_week_df[0]['Среда'] = int(counting[str(fifth_week_date['Среда'])])
                  fifth_week_df[0]['Четверг'] = int(counting[str(fifth_week_date['Четверг'])])
                  fifth_week_df[0]['Пятница'] = int(counting[str(fifth_week_date['Пятница'])])
                  fifth_week_df[0]['Суббота'] = int(counting[str(fifth_week_date['Суббота'])])
                  fifth_week_df[0]['Воскресенье'] = int(counting[str(fourth_week_date['Воскресенье'])])
                  st.dataframe(
                        fifth_week_df,
                        column_config={
                              'Понедельник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Понедельник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Вторник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Вторник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Среда': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1   [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Среда']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Четверг': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Четверг']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Пятница': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Пятница']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Суббота': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Суббота']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Воскресенье': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Воскресенье']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ' )+ 'Воскресенье',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Воскресенье']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                        ),
                  },
            )
            elif fifth_week_df[0]['Суббота'] != '':
                  fifth_week_df[0]['Понедельник'] = int(counting[str(fifth_week_date['Понедельник'])])
                  fifth_week_df[0]['Вторник'] = int(counting[str(fifth_week_date['Вторник'])])
                  fifth_week_df[0]['Среда'] = int(counting[str(fifth_week_date['Среда'])])
                  fifth_week_df[0]['Четверг'] = int(counting[str(fifth_week_date['Четверг'])])
                  fifth_week_df[0]['Пятница'] = int(counting[str(fifth_week_date['Пятница'])])
                  fifth_week_df[0]['Суббота'] = int(counting[str(fifth_week_date['Суббота'])])
                  st.dataframe(
                        fifth_week_df,
                        column_config={
                              'Понедельник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Понедельник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Вторник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Вторник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Среда': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1   [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Среда']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Четверг': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Четверг']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Пятница': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Пятница']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Суббота': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Суббота']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Суббота',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Суббота']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Воскресенье': st.column_config.Column(
                                    '',
                                    width='medium',
                        ),
                  },
            )        
            elif fifth_week_df[0]['Пятница'] != '':
                  fifth_week_df[0]['Понедельник'] = int(counting[str(fifth_week_date['Понедельник'])])
                  fifth_week_df[0]['Вторник'] = int(counting[str(fifth_week_date['Вторник'])])
                  fifth_week_df[0]['Среда'] = int(counting[str(fifth_week_date['Среда'])])
                  fifth_week_df[0]['Четверг'] = int(counting[str(fifth_week_date['Четверг'])])
                  fifth_week_df[0]['Пятница'] = int(counting[str(fifth_week_date['Пятница'])])
                  st.dataframe(
                        fifth_week_df,
                        column_config={
                              'Понедельник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Понедельник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Вторник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Вторник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Среда': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1   [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Среда']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Четверг': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Четверг']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Пятница': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Пятница']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Пятница',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Пятница']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Суббота': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Воскресенье': st.column_config.Column(
                                    '',
                                    width='medium',
                        ),
                  },
            )
            elif fifth_week_df[0]['Четверг'] != '':
                  fifth_week_df[0]['Понедельник'] = int(counting[str(fifth_week_date['Понедельник'])])
                  fifth_week_df[0]['Вторник'] = int(counting[str(fifth_week_date['Вторник'])])
                  fifth_week_df[0]['Среда'] = int(counting[str(fifth_week_date['Среда'])])
                  fifth_week_df[0]['Четверг'] = int(counting[str(fifth_week_date['Четверг'])])
                  st.dataframe(
                        fifth_week_df,
                        column_config={
                              'Понедельник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Понедельник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Вторник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Вторник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Среда': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1   [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Среда']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Четверг': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Четверг']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Четверг',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Четверг']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Пятница': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Суббота': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Воскресенье': st.column_config.Column(
                                    '',
                                    width='medium',
                        ),
                  },
            )
            elif fifth_week_df[0]['Среда'] != '':
                  fifth_week_df[0]['Понедельник'] = int(counting[str(fifth_week_date['Понедельник'])])
                  fifth_week_df[0]['Вторник'] = int(counting[str(fifth_week_date['Вторник'])])
                  fifth_week_df[0]['Среда'] = int(counting[str(fifth_week_date['Среда'])])
                  st.dataframe(
                        fifth_week_df,
                        column_config={
                              'Понедельник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Понедельник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Вторник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Вторник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Среда': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Среда']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else      (st.session_state.select_month1   [:len(st.session_state.select_month1)-1]) + 'я ') + 'Среда',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Среда']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Четверг': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Пятница': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Суббота': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Воскресенье': st.column_config.Column(
                                    '',
                                    width='medium',
                        ),
                  },
            )
            elif fifth_week_df[0]['Вторник'] != '':
                  fifth_week_df[0]['Понедельник'] = int(counting[str(fifth_week_date['Понедельник'])])
                  fifth_week_df[0]['Вторник'] = int(counting[str(fifth_week_date['Вторник'])])
                  st.dataframe(
                        fifth_week_df,
                        column_config={
                              'Понедельник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Понедельник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Вторник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Вторник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Среда': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Четверг': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Пятница': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Суббота': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Воскресенье': st.column_config.Column(
                                    '',
                                    width='medium',
                        ),
                  },
            )
            elif fifth_week_df[0]['Понедельник'] != '':
                  fifth_week_df[0]['Понедельник'] = int(counting[str(fifth_week_date['Понедельник'])])
                  st.dataframe(
                        fifth_week_df,
                        column_config={
                              'Понедельник': st.column_config.ProgressColumn(
                                    str(fifth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                                    width='medium',
                                    format= '%d %s %d' % (int(fifth_week_df[0]['Понедельник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Вторник': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Среда': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Четверг': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Пятница': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Суббота': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Воскресенье': st.column_config.Column(
                                    '',
                                    width='medium',
                        ),
                  },
            )
      except:
            pass
      try:
            if sixth_week_df[0]['Вторник'] != '':
                  sixth_week_df[0]['Понедельник'] = int(counting[str(sixth_week_date['Понедельник'])])
                  sixth_week_df[0]['Вторник'] = int(counting[str(sixth_week_date['Вторник'])])
                  st.dataframe(
                        sixth_week_df,
                        column_config={
                              'Понедельник': st.column_config.ProgressColumn(
                                    str(sixth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                                    width='medium',
                                    format= '%d %s %d' % (int(sixth_week_df[0]['Понедельник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Вторник': st.column_config.ProgressColumn(
                                    str(sixth_week_date['Вторник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август' else    (st.session_state.select_month1 [:len(st.session_state.select_month1)-1]) + 'я ') + 'Вторник',
                                    width='medium',
                                    format= '%d %s %d' % (int(sixth_week_df[0]['Вторник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Среда': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Четверг': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Пятница': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Суббота': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Воскресенье': st.column_config.Column(
                                    '',
                                    width='medium',
                        ),
                  },
            )
            elif sixth_week_df[0]['Понедельник'] != '':
                  sixth_week_df[0]['Понедельник'] = int(counting[str(sixth_week_date['Понедельник'])])
                  st.dataframe(
                        sixth_week_df,
                        column_config={
                              'Понедельник': st.column_config.ProgressColumn(
                                    str(sixth_week_date['Понедельник']) + ' ' + (st.session_state.select_month1[:len(st.session_state.select_month1)-1] + 'та ' if st.session_state.select_month1 == 'Март' or st.session_state.select_month1 == 'Август'     else      (st.session_state.select_month1[:len(st.session_state.select_month1)-1]) + 'я ') + 'Понедельник',
                                    width='medium',
                                    format= '%d %s %d' % (int(sixth_week_df[0]['Понедельник']), 'из', max_worker ),
                                    min_value=0,
                                    max_value=max_worker,
                              ),
                              'Вторник': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Среда': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Четверг': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Пятница': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Суббота': st.column_config.Column(
                                    '',
                                    width='medium',
                              ),
                              'Воскресенье': st.column_config.Column(
                                    '',
                                    width='medium',
                        ),
                  },
            )
      except:
            pass


      
      
