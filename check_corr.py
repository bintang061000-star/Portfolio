import seaborn as sns
import matplotlib.pyplot as plt
import data_prep as dp

# CHECK CORRELATION MATRIX
# check_corr = dp.df_main.corr(numeric_only=True).round(3)
# plt.figure(figsize=(12, 8))
# sns.heatmap(check_corr,
#             annot=True,
#             cmap='coolwarm',
#             center=0,
#             fmt='.2f',)
# plt.title('Correlation Matrix')
# plt.show()

# CHECK INDICATORS
# def check():
#     check = dp.df_main[['Country',
#                         'Living_Cost_Index',
#                         'Tuition_USD',
#                         'Rent_USD',
#                         'Insurance_USD']].groupby('Country').mean().sort_values(by='Tuition_USD', ascending=False).round(2)
#     return check
# print(check())

append_yeCost = dp.append_yeCost(dp.df_main).head())