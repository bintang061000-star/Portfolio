import data_prep as dp

def update_tuiInf():
    us_inflation = dp.get_avgInfTui(dp.df_us)
    uk_inflation = dp.get_avgInfTui(dp.df_uk)
    aus_inflation = dp.get_avgInfTui(dp.df_au)

    tuition_inf = {
        'USA': us_inflation,
        'UK': uk_inflation,
        'Australia': aus_inflation
    }
    return tuition_inf

