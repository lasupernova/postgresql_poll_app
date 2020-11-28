# import libraries
import matplotlib.pyplot as plt
import seaborn as sns

# function to create pie charts
def create_pie_chart(options, values, poll_name):
    # initiate figure
    fig = plt.figure()

    # add one subplot
    axes = fig.add_subplot(1, 1, 1)

    # plot pie chart
    axes.pie(
        values,
        labels = options,
        explode=[0.02]*len(options),
        autopct="%.1f%%",
        colors=sns.color_palette("PuRd",len(options))
    )

    axes.set_title(f'Results for Poll "{poll_name}"')

    # return figure
    return fig
