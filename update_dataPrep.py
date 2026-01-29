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

# df_adjustCheck = df_adjust[['City',
#                             'Living_Cost_Index',
#                             'Exact_Living_Cost',]].groupby('City').mean(numeric_only=True).sort_values(by='Living_Cost_Index', ascending=False).round(2)

# print(df_adjustCheck)

spesifik_df =   df_adjust[
                (df_adjust['Country'] == 'USA') &
                (df_adjust['Tuition_USD'] > 50000) &
                (df_adjust['Level'] == 'Bachelor')]

hasil_kolom = spesifik_df[['City', 'University', 'Level', 'Tuition_USD', 'Exact_Living_Cost']]

print(hasil_kolom)

# print(dp.df_main['Level'].describe())