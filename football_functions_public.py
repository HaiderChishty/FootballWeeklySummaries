import pandas as pd
import numpy as np
from PIL import Image
import urllib
import matplotlib.pyplot as plt

#%%

def fixteamname(series):
    
    series = series.apply(lambda x: (x.replace("HST", 'HOU')))
    series = series.apply(lambda x: (x.replace("CLV", 'CLE')))
    series = series.apply(lambda x: (x.replace("BLT", 'BAL')))
    series = series.apply(lambda x: (x.replace("ARZ", 'ARI')))
    series = series.str.strip()
    
    return series

#%%
def fixname(series):
    
    series = series.apply(lambda x: (x.replace("-", ' ')).lower())
    series = series.apply(lambda x: (x.replace(".", '')))
    series = series.apply(lambda x: (x.replace("'", '')))
    series = series.apply(lambda x: (x.replace("iii", '')))
    series = series.apply(lambda x: (x.replace("ii", '')))
    series = series.apply(lambda x: (x.replace("jr", '')))    
    series = series.str.strip()
    
    return series

#%%
def weekly_recap(week, df, ID_dict, pff_receiving, pff_passing):
    
    Week_df = df.query("week == @week")
    Week_dropbacks_perteam_df = pff_passing[['team_name','dropbacks']].groupby('team_name').sum()
    Week_TeamStats_df = Week_df[['recent_team','completions', 'attempts', 'passing_yards', 'passing_tds', 'interceptions', 
                                             'passing_air_yards', 'passing_yards_after_catch', 'carries', 'rushing_yards', 
                                             'rushing_tds', 'fantasy_points_ppr']].groupby('recent_team').sum()
    Week_TeamStats_df = pd.merge(Week_TeamStats_df,Week_dropbacks_perteam_df, left_index = True, right_index = True)
    Week_TeamStats_df.rename(columns={"carries": "team_carries", "dropbacks": "team_dropbacks"}, inplace = True)


    Week_QBs_df = Week_df.query("position == 'QB'")[['name','recent_team','completions', 
                                                       'attempts', 'passing_air_yards', 'passing_yards', 'passing_yards_after_catch',
                                                       'passing_tds', 'interceptions',
                                                       'carries', 'rushing_yards', 'rushing_tds','fantasy_points_ppr']]

    Week_QBs_df = pd.merge(Week_QBs_df,Week_TeamStats_df[['team_carries']], 
                            left_on = ['recent_team'], right_index = True)
    Week_QBs_df['completion_percentage'] = Week_QBs_df['completions']/Week_QBs_df['attempts']
    Week_QBs_df['yards_per_attempt'] = Week_QBs_df['passing_yards']/Week_QBs_df['attempts']
    Week_QBs_df['yards_after_catch_percentage'] = Week_QBs_df['passing_yards_after_catch']/Week_QBs_df['passing_yards']
    Week_QBs_df['adot'] = Week_QBs_df['passing_air_yards']/Week_QBs_df['attempts']
    Week_QBs_df['percent_carries'] = Week_QBs_df['carries']/Week_QBs_df['team_carries']
    Week_QBs_df['yards_per_carry'] = Week_QBs_df['rushing_yards']/Week_QBs_df['carries']
    Week_QBs_df['week'] = week
    
    ##
    Week_WRs_df = Week_df.query("position == 'WR'")[['name','recent_team', 'receptions', 'targets', 
                                                       'receiving_yards', 'receiving_tds', 'receiving_air_yards', 
                                                       'carries', 'rushing_yards', 'rushing_tds','fantasy_points_ppr']]

    Week_WRs_df = pd.merge(Week_WRs_df,Week_TeamStats_df[['attempts','passing_air_yards','team_carries','team_dropbacks']], 
                            left_on = ['recent_team'], right_index = True)

    Week_WRs_df = pd.merge(Week_WRs_df,pff_receiving[['player','routes','yprr']], 
                            left_on = ['name'], right_on = ['player'])
    Week_WRs_df.drop('player', axis=1, inplace=True)

    Week_WRs_df.rename(columns={"attempts": "team_pass_attempts",'passing_air_yards': 'team_air_yards', 'yprr': 'yards_per_route_run',
                                'routes': 'routes_run'}, inplace = True)

    Week_WRs_df['target_share'] = Week_WRs_df['targets']/Week_WRs_df['team_pass_attempts']
    Week_WRs_df['air_yard_share'] = Week_WRs_df['receiving_air_yards']/Week_WRs_df['team_air_yards']
    Week_WRs_df['adot'] = Week_WRs_df['receiving_air_yards']/Week_WRs_df['targets']
    Week_WRs_df['targets_per_route_run'] = Week_WRs_df['targets']/Week_WRs_df['routes_run']
    Week_WRs_df['routes_run_per_team_dropback'] = Week_WRs_df['routes_run']/Week_WRs_df['team_dropbacks']   
    Week_WRs_df['yards_per_target'] = Week_WRs_df['receiving_yards']/Week_WRs_df['targets']
    Week_WRs_df['percent_carries'] = Week_WRs_df['carries']/Week_WRs_df['team_carries']
    Week_WRs_df['yards_per_carry'] = Week_WRs_df['rushing_yards']/Week_WRs_df['carries']
    Week_WRs_df['week'] = week
        
    ##
    Week_TEs_df = Week_df.query("position == 'TE'")[['name','recent_team', 'receptions', 'targets', 
                                                       'receiving_yards', 'receiving_tds', 'receiving_air_yards', 
                                                       'carries', 'rushing_yards', 'rushing_tds','fantasy_points_ppr']]

    Week_TEs_df = pd.merge(Week_TEs_df,Week_TeamStats_df[['attempts','passing_air_yards','team_carries','team_dropbacks']], 
                            left_on = ['recent_team'], right_index = True)
    
    Week_TEs_df = pd.merge(Week_TEs_df,pff_receiving[['player','routes','yprr']], 
                            left_on = ['name'], right_on = ['player'])
    Week_TEs_df.drop('player', axis=1, inplace=True)

    Week_TEs_df.rename(columns={"attempts": "team_pass_attempts",'passing_air_yards': 'team_air_yards', 'yprr': 'yards_per_route_run',
                                'routes': 'routes_run'}, inplace = True)

    Week_TEs_df['target_share'] = Week_TEs_df['targets']/Week_TEs_df['team_pass_attempts']
    Week_TEs_df['air_yard_share'] = Week_TEs_df['receiving_air_yards']/Week_TEs_df['team_air_yards']
    Week_TEs_df['adot'] = Week_TEs_df['receiving_air_yards']/Week_TEs_df['targets']
    Week_TEs_df['targets_per_route_run'] = Week_TEs_df['targets']/Week_TEs_df['routes_run']
    Week_TEs_df['routes_run_per_team_dropback'] = Week_TEs_df['routes_run']/Week_TEs_df['team_dropbacks']   
    Week_TEs_df['yards_per_target'] = Week_TEs_df['receiving_yards']/Week_TEs_df['targets']
    Week_TEs_df['percent_carries'] = Week_TEs_df['carries']/Week_TEs_df['team_carries']
    Week_TEs_df['yards_per_carry'] = Week_TEs_df['rushing_yards']/Week_TEs_df['carries']
    Week_TEs_df['week'] = week

    ##
    Week_RBs_df = Week_df.query("position == 'RB'")[['name','recent_team', 'carries', 'rushing_yards', 'rushing_tds', 
                                                       'receptions', 'targets', 
                                                       'receiving_yards', 'receiving_tds', 'receiving_air_yards', 
                                                       'fantasy_points_ppr']]

    Week_RBs_df = pd.merge(Week_RBs_df,Week_TeamStats_df[['attempts','passing_air_yards', 'team_carries','team_dropbacks']], 
                            left_on = ['recent_team'], right_index = True)
    
    Week_RBs_df = pd.merge(Week_RBs_df,pff_receiving[['player','routes','yprr']], 
                            left_on = ['name'], right_on = ['player'], how = 'left')
    Week_RBs_df.drop('player', axis=1, inplace=True)
    Week_RBs_df.fillna(0, inplace=True)

    Week_RBs_df.rename(columns={"attempts": "team_pass_attempts",'passing_air_yards': 'team_air_yards', 'yprr': 'yards_per_route_run',
                                'routes': 'routes_run'}, inplace = True)

    Week_RBs_df['target_share'] = Week_RBs_df['targets']/Week_RBs_df['team_pass_attempts']
    Week_RBs_df['air_yard_share'] = Week_RBs_df['receiving_air_yards']/Week_RBs_df['team_air_yards']
    Week_RBs_df['adot'] = Week_RBs_df['receiving_air_yards']/Week_RBs_df['targets']
    Week_RBs_df['targets_per_route_run'] = Week_RBs_df['targets']/Week_RBs_df['routes_run']
    Week_RBs_df['routes_run_per_team_dropback'] = Week_RBs_df['routes_run']/Week_RBs_df['team_dropbacks']   
    Week_RBs_df['yards_per_target'] = Week_RBs_df['receiving_yards']/Week_RBs_df['targets']
    Week_RBs_df['percent_carries'] = Week_RBs_df['carries']/Week_RBs_df['team_carries']
    Week_RBs_df['yards_per_carry'] = Week_RBs_df['rushing_yards']/Week_RBs_df['carries']
    Week_RBs_df['week'] = week

    ##
    Week = dict(zip(Week_TeamStats_df.index, [None]*len(Week_TeamStats_df.index)))
    
    for team in Week.keys():
        Week[team] = {"passing": Week_QBs_df.query("recent_team==@team")[['name','fantasy_points_ppr',
                                                                            'passing_yards','passing_tds','completions',
                                                                            'attempts','completion_percentage','yards_per_attempt','adot']],
                       "receiving": pd.concat([Week_WRs_df.query("recent_team==@team")[['name',
                                                'fantasy_points_ppr','routes_run_per_team_dropback','receiving_yards','receiving_tds',
                                                'receptions','targets','target_share','yards_per_route_run','targets_per_route_run',
                                                'adot','receiving_air_yards','air_yard_share']],Week_TEs_df.query("recent_team==@team")[[
                                                    'name','fantasy_points_ppr','routes_run_per_team_dropback','receiving_yards','receiving_tds',
                                                    'receptions','targets','target_share','yards_per_route_run','targets_per_route_run',
                                                    'adot','receiving_air_yards','air_yard_share']],
                                                    Week_RBs_df.query("recent_team==@team")[[
                                                        'name','fantasy_points_ppr','routes_run_per_team_dropback','receiving_yards','receiving_tds',
                                                        'receptions','targets','target_share','yards_per_route_run','targets_per_route_run',
                                                        'adot','receiving_air_yards','air_yard_share']]]),
                       "rushing": pd.concat([Week_RBs_df.query("recent_team==@team")[[
                           'name','fantasy_points_ppr','carries','rushing_yards','rushing_tds','percent_carries']],
                           Week_QBs_df.query("recent_team==@team")[[
                               'name','fantasy_points_ppr','carries','rushing_yards','rushing_tds','percent_carries']],
                           Week_WRs_df.query("recent_team==@team")[[
                               'name','fantasy_points_ppr','carries','rushing_yards','rushing_tds','percent_carries']],
                           Week_TEs_df.query("recent_team==@team")[[
                               'name','fantasy_points_ppr','carries','rushing_yards','rushing_tds','percent_carries']]])}
                                                    
    Week_QB_summary = Week_QBs_df[['name','fantasy_points_ppr','passing_yards',
                                  'passing_tds','completions','attempts','completion_percentage',
                                  'yards_per_attempt','adot','carries','rushing_yards','rushing_tds','percent_carries']]

    Week_WR_summary =  Week_WRs_df[['name','fantasy_points_ppr','receiving_yards','receiving_tds',
                             'receptions','targets','target_share',
                             'adot','receiving_air_yards','air_yard_share','carries','rushing_yards','rushing_tds','percent_carries']]

    Week_TE_summary =  Week_TEs_df[['name','fantasy_points_ppr','receiving_yards','receiving_tds',
                             'receptions','targets','target_share',
                             'adot','receiving_air_yards','air_yard_share','carries','rushing_yards','rushing_tds','percent_carries']]
                                     
    Week_RB_summary = Week_RBs_df[['name','fantasy_points_ppr','carries','rushing_yards','rushing_tds','percent_carries',
                                     'receiving_yards','receiving_tds',
                                     'receptions','targets','target_share',
                                     'adot','receiving_air_yards','air_yard_share',]]
    
    return Week, Week_QB_summary, Week_WR_summary, Week_TE_summary, Week_RB_summary, Week_QBs_df, Week_WRs_df, Week_TEs_df, Week_RBs_df

#%%
def plot_pass_recap(team,Week,team_plot,headshot_dict,save):
  
    # passing
    df_passing = team_plot['passing']    
    df_passing.dropna(subset=['adot'], inplace = True)
    
    df_passing['completion_percentage'] = 100*df_passing['completion_percentage']
    df_passing['completion_percentage'] = df_passing['completion_percentage'].round(0)
    df_passing['completion_percentage'] = df_passing[
    'completion_percentage'].astype(int).astype(str).apply(lambda x: (x+'%'))
    
    df_passing[['yards_per_attempt','adot']] = df_passing[[
        'yards_per_attempt','adot']].round(2)
    df_passing['yards_per_attempt'] = df_passing[
        'yards_per_attempt'].apply(lambda x: format(x,'.2f'))
    df_passing['adot'] = df_passing[
            'adot'].apply(lambda x: format(x,'.2f'))
    
    df_passing['passing_yards'] = df_passing['passing_yards'].astype(int)
                                      
    df_passing.sort_values(by='attempts', inplace = True)
    df_passing.reset_index(inplace = True,drop = True)
    df_passing['headshot'] = df_passing['name'].map(headshot_dict)
    
    ncols = df_passing.shape[1]
    nrows = df_passing.shape[0]
    col1_pos = 4.5
    fig = plt.figure(num=1, clear=True, figsize=(1.25*ncols+col1_pos-1,nrows), dpi=300)
    ax = plt.subplot()
    ax.set_xlim(0, 1.25*ncols + col1_pos+1)
    ax.set_ylim(0, nrows + 1)
    positions = [1]+np.linspace(col1_pos, 1.25*ncols + col1_pos, num=ncols-2).tolist()
    columns = ['name','fantasy_points_ppr','passing_yards','passing_tds','completions',
                             'attempts','completion_percentage','yards_per_attempt',
                             'adot']
    for i in range(nrows):
        for j, column in enumerate(columns):
            if j == 0:
                ha = 'left'
            else:
                ha = 'center'
            if column == 'name':
                weight = 'bold'
            else:
                weight = 'normal'
            ax.annotate(
                xy=(positions[j], i + .5),
                text=df_passing[column].iloc[i],
                ha=ha,
                va='center',
                weight=weight,
                fontsize = 15
            )
    DC_to_FC = ax.transData.transform
    FC_to_NFC = fig.transFigure.inverted().transform
    DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))
    ax_point_1 = DC_to_NFC([0.25, 0.25])
    ax_point_2 = DC_to_NFC([0.75, 0.75])
    ax_width = abs(ax_point_1[0] - ax_point_2[0])*1.5
    ax_height = abs(ax_point_1[1] - ax_point_2[1])*1.5
    for x in df_passing.index:
        if df_passing['headshot'][x] != None:
            ax_coords = DC_to_NFC([0.15, x + .2])
            hs_ax = fig.add_axes([ax_coords[0], ax_coords[1], ax_width, ax_height])
            ax_headshot(df_passing['headshot'][x], hs_ax)
    column_names = ['Name','Fantasy\nPoints','Passing\n Yards','Passing\nTDs',
                    'Comp.','Att.','Comp. Perc.','YPA',
                    'ADOT']
    for index, c in enumerate(column_names):
            if index == 0:
                ha = 'left'
            else:
                ha = 'center'
            ax.annotate(
                xy=(positions[index], nrows + 0.25),
                text=column_names[index],
                ha=ha,
                va='bottom',
                weight='bold',
                fontsize = 15
            )
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]+50], [nrows, nrows], lw=1.5, color='black', marker='', zorder=4)
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]+50], [0, 0], lw=1.5, color='black', marker='', zorder=4)
    for x in range(1, nrows):
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]+50], [x, x], lw=1.15, color='gray', ls=':', zorder=3 , marker='')
    ax.set_axis_off()    
    if save == 1:
        plt.savefig('D:/OneDrive/Documents/Python Scripts/football/Summaries/2024 Charts/Week '+str(Week)+'/'+team+' Passing.png',
                    bbox_inches='tight')
        
#%% 
def plot_rec_recap(team,Week,team_plot,headshot_dict,save):
                       
    df_receiving = team_plot['receiving'].query("routes_run_per_team_dropback>0")
    
    df_receiving.drop(['adot','receiving_air_yards','air_yard_share'], axis=1, inplace = True)
    
    df_receiving[['routes_run_per_team_dropback','target_share']] = 100*df_receiving[[
        'routes_run_per_team_dropback','target_share']]
    df_receiving[['routes_run_per_team_dropback','target_share']] = df_receiving[[
        'routes_run_per_team_dropback','target_share']].round(0) 
    df_receiving.sort_values(by='routes_run_per_team_dropback', inplace = True)
    df_receiving[['routes_run_per_team_dropback','target_share']] = df_receiving[[
             'routes_run_per_team_dropback','target_share']].astype(int).astype(str).apply(lambda x: (x+'%'))
    
    df_receiving[['targets_per_route_run','yards_per_route_run']] = df_receiving[[
        'targets_per_route_run','yards_per_route_run']].round(2)
    df_receiving['targets_per_route_run'] = df_receiving[
        'targets_per_route_run'].apply(lambda x: format(x,'.2f'))
    df_receiving['yards_per_route_run'] = df_receiving[
        'yards_per_route_run'].apply(lambda x: format(x,'.2f'))
    
    df_receiving['receiving_yards'] = df_receiving['receiving_yards'].astype(int)
                                     
    df_receiving.reset_index(inplace = True,drop = True)
    df_receiving['headshot'] = df_receiving['name'].map(headshot_dict)
    
    ncols = df_receiving.shape[1]
    nrows = df_receiving.shape[0]
    col1_pos = 4.5
    fig = plt.figure(num=1, clear=True, figsize=(1.25*ncols+col1_pos-1,nrows), dpi=300)
    ax = plt.subplot()
    ax.set_xlim(0, 1.25*ncols + col1_pos+1)
    ax.set_ylim(0, nrows + 1)
    positions = [1]+np.linspace(col1_pos, 1.25*ncols + col1_pos, num=ncols-2).tolist()
    columns = ['name','fantasy_points_ppr','routes_run_per_team_dropback','receiving_yards','receiving_tds',
                             'receptions','targets','target_share','targets_per_route_run','yards_per_route_run']
    for i in range(nrows):
        for j, column in enumerate(columns):
            if j == 0:
                ha = 'left'
            else:
                ha = 'center'
            if column == 'routes_run_per_team_dropback' or column == 'name':
                weight = 'bold'
            else:
                weight = 'normal'
            fontsize = 15
            if column == 'name':
                fontsize = 12
            ax.annotate(
                xy=(positions[j], i + .5),
                text=df_receiving[column].iloc[i],
                ha=ha,
                va='center',
                weight=weight,
                fontsize = fontsize
            )
    DC_to_FC = ax.transData.transform
    FC_to_NFC = fig.transFigure.inverted().transform
    DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))
    ax_point_1 = DC_to_NFC([0.25, 0.25])
    ax_point_2 = DC_to_NFC([0.75, 0.75])
    ax_width = abs(ax_point_1[0] - ax_point_2[0])*1.5
    ax_height = abs(ax_point_1[1] - ax_point_2[1])*1.5
    for x in df_receiving.index:
        if df_receiving['headshot'][x] != None:
            ax_coords = DC_to_NFC([0.15, x + .2])
            hs_ax = fig.add_axes([ax_coords[0], ax_coords[1], ax_width, ax_height])
            ax_headshot(df_receiving['headshot'][x], hs_ax)
    column_names = ['Name','Fantasy\nPoints','Routes\n Run','Rec.\nYards','Rec.\nTDs','Rec.',
                                    'Targets','Target\nShare','TPRR','YPRR']
                   
    for index, c in enumerate(column_names):
            if index == 0:
                ha = 'left'
            else:
                ha = 'center'
            ax.annotate(
                xy=(positions[index], nrows + 0.25),
                text=column_names[index],
                ha=ha,
                va='bottom',
                weight='bold',
                fontsize = 15
            )
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]+50], [nrows, nrows], lw=1.5, color='black', marker='', zorder=4)
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]+50], [0, 0], lw=1.5, color='black', marker='', zorder=4)
    for x in range(1, nrows):
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]+50], [x, x], lw=1.15, color='gray', ls=':', zorder=3 , marker='')
    ax.set_axis_off()
    if save == 1:
        plt.savefig('D:/OneDrive/Documents/Python Scripts/football/Summaries/2024 Charts/Week '+str(Week)+'/'+team+' Receiving.png',
                    bbox_inches='tight')

#%%
def plot_rush_recap(team,Week,team_plot,headshot_dict,save):
    
    # rushing
    df_rushing = team_plot['rushing'].query("carries>0")
    
    df_rushing['percent_carries'] = 100*df_rushing['percent_carries']
    df_rushing['percent_carries'] = df_rushing['percent_carries'].round(0)
    df_rushing['percent_carries'] = df_rushing[
        'percent_carries'].astype(int).astype(str).apply(lambda x: (x+'%'))
    
    df_rushing['rushing_yards'] = df_rushing['rushing_yards'].astype(int)
                                      
    df_rushing.sort_values(by='carries', inplace = True)
    df_rushing.reset_index(inplace = True,drop = True)
    df_rushing['headshot'] = df_rushing['name'].map(headshot_dict)
    
    ncols = df_rushing.shape[1]
    nrows = df_rushing.shape[0]
    col1_pos = 5.5
    fig = plt.figure(num=1, clear=True, figsize=(1*ncols+col1_pos-1,nrows), dpi=300)
    ax = plt.subplot()
    ax.set_xlim(0, 1*ncols + col1_pos+1)
    ax.set_ylim(0, nrows + 1)
    positions = [1]+np.linspace(col1_pos, 1*ncols + col1_pos, num=ncols-2).tolist()
    columns = ['name','fantasy_points_ppr','carries','rushing_yards','rushing_tds',
                             'percent_carries']
    for i in range(nrows):
        for j, column in enumerate(columns):
            if j == 0:
                ha = 'left'
            else:
                ha = 'center'
            if column == 'name' or column == 'carries':
                weight = 'bold'
            else:
                weight = 'normal'
            ax.annotate(
                xy=(positions[j], i + .5),
                text=df_rushing[column].iloc[i],
                ha=ha,
                va='center',
                weight=weight,
                fontsize = 15
            )
    DC_to_FC = ax.transData.transform
    FC_to_NFC = fig.transFigure.inverted().transform
    DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))
    ax_point_1 = DC_to_NFC([0.25, 0.25])
    ax_point_2 = DC_to_NFC([0.75, 0.75])
    ax_width = abs(ax_point_1[0] - ax_point_2[0])*1.5
    ax_height = abs(ax_point_1[1] - ax_point_2[1])*1.5
    for x in df_rushing.index:
        if df_rushing['headshot'][x] != None:
            ax_coords = DC_to_NFC([0.15, x + .2])
            hs_ax = fig.add_axes([ax_coords[0], ax_coords[1], ax_width, ax_height])
            ax_headshot(df_rushing['headshot'][x], hs_ax)
    column_names = ['Name','Fantasy\nPoints','Carries','Rush.\n Yards','Rush.\nTDs',
                    'Carry %']
    for index, c in enumerate(column_names):
            if index == 0:
                ha = 'left'
            else:
                ha = 'center'
            ax.annotate(
                xy=(positions[index], nrows + 0.25),
                text=column_names[index],
                ha=ha,
                va='bottom',
                weight='bold',
                fontsize = 15
            )
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]+50], [nrows, nrows], lw=1.5, color='black', marker='', zorder=4)
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]+50], [0, 0], lw=1.5, color='black', marker='', zorder=4)
    for x in range(1, nrows):
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]+50], [x, x], lw=1.15, color='gray', ls=':', zorder=3 , marker='')
    ax.set_axis_off()
    if save == 1:
        plt.savefig('D:/OneDrive/Documents/Python Scripts/football/Summaries/2024 Charts/Week '+str(Week)+'/'+team+' Rushing.png',
                    bbox_inches='tight')
        
#%%
def ax_headshot(hs_df, ax):
    '''
    Plots the logo of the team at a specific axes.
    Args:
        team_id (int): the id of the team according to Fotmob. You can find it in the url of the team page.
        ax (object): the matplotlib axes where we'll draw the image.
    '''
    hs_url = hs_df
    headshot = Image.open(urllib.request.urlopen(hs_url))
    ax.imshow(headshot)
    ax.axis('off')
    return ax