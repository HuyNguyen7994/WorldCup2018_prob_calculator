# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 21:13:04 2018

@author: HuyNguyen
"""

import pandas
from bs4 import BeautifulSoup
import requests
from copy import deepcopy
import re
import numpy

def get_page(page_link):
    return requests.get(page_link).content

def get_table(page):
    page_soup = BeautifulSoup(page, "html5lib")
    table = page_soup.find("table",{"class":"eventTable"})
    return table

#start from here 
def get_odd_table(match):
    page = get_page(match)
    table = get_table(page)
    table = table.find("tbody")
    rows = table.find_all("tr")
    result_array = []
    for row in rows:
        temp = []
        row = row.find_all("td")
        name = row[0].text
        if name == "Any Other Score":
            continue
        temp.append(name)
        temp += [cell.text for cell in row[1:]]
        result_array.append(temp)
    return result_array

def odd_to_prob(odd):
    if not odd:
        return 0
    if "/" in odd:
        a,b = odd.split("/")
        a,b = int(a), int(b)
    else:
        a,b = int(odd), 1
    prob = b/(a+b)
    return prob
     
def get_prob_table(odd_table):
    rows = deepcopy(odd_table)
    # process the odd
    rows = [["name"] + [f"bookie{i}" for i in range(1, len(rows[0]))] + ["winner", "winner_score", "loser_score"]] + rows
    for row in rows[1:]:
        for i in range(1,len(row)):
            row[i] = odd_to_prob(row[i])
        # process the scenarios
        pattern = re.compile(r"([A-Za-z ]+) (\d+)-(\d+)")
        matches = re.match(pattern, row[0])
        winner, winner_score, loser_score = matches.group(1,2,3)
        row += [winner, int(winner_score), int(loser_score)]
    data = pandas.DataFrame(rows)
    data.columns = data.iloc[0]
    data = data.iloc[1:]
    return data

def get_bookie_prob_table(prob_table):
    table = prob_table
    # weight bookie probability
    for name in table:
        if 'bookie' in name:
            weight = sum(table[name])
            if weight == 0:
                continue
            table[name] = table[name] / weight
    return table

def adj_prob_table(bookie_prob_table, adj_team, adj_score):
    table = bookie_prob_table
    teams = list(table.winner.unique())
    teams.remove(adj_team)
    teams.remove("Draw")
    other_team = teams[0]
    table["margin"] = table["winner_score"] - table["loser_score"] - adj_score
    table["adj_result"] = table["winner"]
    for i in range(1,len(table)):
        if table.at[i, "winner"] == other_team:
            continue
        margin = table.at[i,"margin"]
        if margin == 0:
            table.at[i, "adj_result"] = "Draw"
        elif margin < 0:
            table.at[i, "adj_result"] = other_team
        elif margin > 0:
            table.at[i, "adj_result"] = adj_team
        else:
            print(margin, i)
            raise
    return table
    
def get_result(adj_prob):
    table = adj_prob
    scenarios = table.adj_result.unique()
    final_result = {}
    for scenario in scenarios:
        average_prob = []
        all_prob = table[(table.adj_result == scenario)]
        for name in all_prob:
            if "bookie" in name:
                prob = sum(all_prob[name])
                average_prob.append(prob)
        average_prob = numpy.mean(average_prob)
        final_result[scenario] = average_prob
    weight_prob = sum(final_result.values())
    for scenario in final_result:
        final_result[scenario] = final_result[scenario] / weight_prob
    return final_result
                
# use this function
def calculate_result(match, adj_team, adj_score):
    link = f"https://www.oddschecker.com/football/world-cup/{match}/correct-score"
    odd_table = get_odd_table(link)
    prob_table = get_prob_table(odd_table)
    bookie_prob_table = get_bookie_prob_table(prob_table)
    adj_prob = adj_prob_table(bookie_prob_table,adj_team,adj_score)
    result = get_result(adj_prob)
    for scenario in result:
        print(scenario,result[scenario])
    return odd_table ,prob_table, bookie_prob_table, adj_prob, result

# odd_table ,prob_table, bookie_prob_table, adj_prob, result = calculate_result("costa-rica-v-serbia", "Costa Rica", 1.0)
