import data_prep as dp

# def update_tuiInf():
#     us_inflation = dp.get_avgInfTui(dp.df_us)
#     uk_inflation = dp.get_avgInfTui(dp.df_uk)
#     aus_inflation = dp.get_avgInfTui(dp.df_au)

#     tuition_inf = {
#         'USA': us_inflation,
#         'UK': uk_inflation,
#         'Australia': aus_inflation
#     }
#     return tuition_inf

df_adjust = (dp.df_work
           .pipe(dp.append_yeCost)
           .pipe(dp.update_data)
           .pipe(dp.exact_livCost)
            )

df_adjustCheck = df_adjust[['Country',
                       'City',
                       'Living_Cost_Index',
                       'Exact_Living_Cost',]].groupby('Country').mean(numeric_only=True).sort_values(by='Living_Cost_Index', ascending=False).round(2)

print(df_adjustCheck)