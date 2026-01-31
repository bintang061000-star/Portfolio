import seaborn as sns
import matplotlib.pyplot as plt
import data_prep as dp

# CHECK CORRELATION MATRIX
check_corr = dp.df_main.corr(numeric_only=True).round(3)
plt.figure(figsize=(12, 8))
sns.heatmap(check_corr,
            annot=True,
            cmap='coolwarm',
            center=0,
            fmt='.2f',)
plt.title('Correlation Matrix')
plt.show()