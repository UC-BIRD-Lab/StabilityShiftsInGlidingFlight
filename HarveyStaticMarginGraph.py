import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

font_dict=dict(family='Arial',
               size=28,
               color='black'
               )
dat_comp = pd.read_csv("*Insert pathname*/2023_04_14_compdata.csv") #Harvey's original species data
SM_data_3D = pd.read_csv("*Insert pathname*/SM_data_3D_WindTunnelData.csv") #My Harris' Hawk maximum static margin bound data
standard_error = pd.read_csv('*Insert pathname*/SMdataMedium.csv')

#################################

max_sm_bounds = standard_error[standard_error['CMcgα/CLαmean'] == standard_error['CMcgα/CLαmean'].max()]
min_sm_bounds = standard_error[standard_error['CMcgα/CLαmean'] == standard_error['CMcgα/CLαmean'].min()]

original_point_max = max_sm_bounds['CMcgα/CLαmean']
lower_bound_max = max_sm_bounds['CMcgα/CLαmean'] - max_sm_bounds['CMcgα/CLαsd']
upper_bound_max = max_sm_bounds['CMcgα/CLαmean'] + max_sm_bounds['CMcgα/CLαsd']

original_point_min = min_sm_bounds['CMcgα/CLαmean']
lower_bound_min = min_sm_bounds['CMcgα/CLαmean'] - min_sm_bounds['CMcgα/CLαsd']
upper_bound_min = min_sm_bounds['CMcgα/CLαmean'] + min_sm_bounds['CMcgα/CLαsd']

############################################

#Close relatives

#Hawks

hawk_rows = dat_comp[dat_comp['binomial'].str.contains('Accipiter')]


#Owls

owl_rows = dat_comp[dat_comp['binomial'].str.contains('Tyto')]


#The rest

dat_comp = dat_comp.drop(hawk_rows.index)
dat_comp = dat_comp.drop(owl_rows.index)

###############################################

# Create figure
fig = px.line(template='simple_white')

x=dat_comp['full_m']
y=dat_comp['max_sm_nd']
# Add traces

fig.add_trace(go.Scatter(x=dat_comp['full_m'], y=dat_comp['max_sm_nd'], mode='markers', marker=dict(color='gray', size=7, symbol='square', line=dict(width=1, color='gray')), name=None))
fig.add_trace(go.Scatter(x=dat_comp['full_m'], y=dat_comp['min_sm_nd'], mode='markers', marker=dict(color='gray', size=7, symbol='square', line=dict(width=1, color='gray')), name=None))
fig.add_trace(go.Scatter(x=dat_comp['full_m'], y=(dat_comp['max_sm_nd']+dat_comp['min_sm_nd'])/2, mode='markers', marker=dict(color='rgba(0,0,0,0)', size=4, symbol='circle-open', line=dict(width=1, color='gray')), error_y=dict(type='data', array=(dat_comp['max_sm_nd']-dat_comp['min_sm_nd'])/2, color='gray'), name=None))

fig.add_trace(go.Scatter(x=owl_rows['full_m'], y=owl_rows['max_sm_nd'], mode='markers', marker=dict(color='#f4c04d', size=7, symbol='square', line=dict(width=4, color='#f4c04d'), opacity=1), name=None))
fig.add_trace(go.Scatter(x=owl_rows['full_m'], y=owl_rows['min_sm_nd'], mode='markers', marker=dict(color='#f4c04d', size=7, symbol='square', line=dict(width=4, color='#f4c04d'), opacity=1), name=None))
fig.add_trace(go.Scatter(x=owl_rows['full_m'], y=(owl_rows['max_sm_nd']+owl_rows['min_sm_nd'])/2, mode='markers', marker=dict(color='rgba(0,0,0,0)', size=4, symbol='circle-open', line=dict(width=1, color='#f4c04d')), error_y=dict(type='data', array=(owl_rows['max_sm_nd']-owl_rows['min_sm_nd'])/2, color='#f4c04d', thickness = 4), name=None))

fig.add_trace(go.Scatter(x=hawk_rows['full_m'], y=hawk_rows['max_sm_nd'], mode='markers', marker=dict(color='#e68e56', size=7, symbol='square', line=dict(width=4, color='#e68e56'), opacity=1), name=None))
fig.add_trace(go.Scatter(x=hawk_rows['full_m'], y=hawk_rows['min_sm_nd'], mode='markers', marker=dict(color='#e68e56', size=7, symbol='square', line=dict(width=4, color='#e68e56'), opacity=1), name=None))
fig.add_trace(go.Scatter(x=hawk_rows['full_m'], y=(hawk_rows['max_sm_nd']+hawk_rows['min_sm_nd'])/2, mode='markers', marker=dict(color='rgba(0,0,0,0)', size=4, symbol='circle-open', line=dict(width=1, color='#e68e56')), error_y=dict(type='data', array=(hawk_rows['max_sm_nd']-hawk_rows['min_sm_nd'])/2, color='#e68e56', thickness = 4), name=None))

fig.add_trace(go.Scatter(x=SM_data_3D['full_m'], y=SM_data_3D['max_sm_nd'], mode='markers', marker=dict(color='#c55e71', size=7, symbol='square', line=dict(width=4, color='#c55e71'), opacity=1), name=None))
fig.add_trace(go.Scatter(x=SM_data_3D['full_m'], y=SM_data_3D['min_sm_nd'], mode='markers', marker=dict(color='#c55e71', size=7, symbol='square', line=dict(width=4, color='#c55e71'), opacity=1), name=None))
fig.add_trace(go.Scatter(x=SM_data_3D['full_m'], y=(SM_data_3D['max_sm_nd']+SM_data_3D['min_sm_nd'])/2, mode='markers', marker=dict(color='rgba(0,0,0,0)', size=4, symbol='circle-open', line=dict(width=1, color='#c55e71')), error_y=dict(type='data', array=(SM_data_3D['max_sm_nd']-SM_data_3D['min_sm_nd'])/2, color='#c55e71', thickness = 4), name=None))

# Update layout
fig.update_layout(xaxis_type='log', xaxis_range=[-2.1, 1.1], xaxis_title='Body mass (kg)',xaxis_exponentformat = 'power', xaxis_showexponent = 'all')
fig.update_layout(
    yaxis={'title': 'Normalized static margin <br>(% of c<sub>r<sub>max</sub></sub>)'},
    showlegend=False, yaxis_range=[-0.63,0.63]
)
fig.update_xaxes(dtick=1)

# Remove axis lines
fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                 tickcolor='black')
fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                 tickcolor='black')

# Remove gridlines
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)

fig.update_layout(
    shapes=[
        {
            'type': 'rect',
            'xref': 'paper',
            'yref': 'paper',
            'x0': 0.25,
            'y0': 0.5,
            'x1': 0.75,
            'y1': 0.75,
            'fillcolor': 'grey',
            'opacity': 0.2,
            'line': {'width': 0}
        }
    ]
)

# Set font and size for title and axis labels
fig.update_layout(font=font_dict,  # font formatting
                    # remove white space
                  )
fig.update_layout(width=1500, height=1000)
fig.update_xaxes(domain=(0.25,0.75))
fig.update_yaxes(domain=(0.5,1))
fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))


# Show plot
fig.show()

# fig.write_image("*Insert pathname*.pdf")
#fig.write_image("*Insert pathname*.pdf")
