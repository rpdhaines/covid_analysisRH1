# File containing the markdown strings for all substantive text in the app

# information text at bottom of all pages
main_info = '''
    This app is provided 'as is' without warranty of any kind. No reliance can be placed on the contents of this app. The data used is public data from:  
    The gov.uk coronavirus dashboard [https://coronavirus.data.gov.uk/]  
    The data accessed from the coronavirus dashboard is cases by specimen date, available as a csv download from
     [https://api.coronavirus.data.gov.uk/v2/data?areaType=region&metric=newCasesBySpecimenDateAgeDemographics&format=csv]  
    The ONS 2019 population estimates available from [https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland]  
    The code for this app can be found on GitHub: [https://github.com/rpdhaines/covid_analysisRH1]  
    Questions? Contact me on rpdhaines2@yahoo.co.uk 
    '''


# text for Information tab
tab0_info = """
### This dashboard has been created in Plotly Dash by Richard Haines.  
Last updated: July 2021  
### About the author  
I am a mathematician with a love for data science and analytics. Having spent much of my career as an actuary, I have
been transitioning to more pure analytics and data science roles with an ambition to use my skills in ways that 
benefit society. I've recently relocated from London to the Netherlands with my family.  
  
### About the dashboard  
This dashboard allows the user to perform some basic exploratory analysis of some of the publicly available England
COVID data.  
There are 3 tabs looking at relationships between vaccination coverage, cases and hospital admissions. Analysis can 
be filtered by age groups, regions and time period. And there are a few other parameters to play with.  
Explore the tabs and see what you can discover. Have fun!  
"""

# tab for info box 1 on 'case analysis by age and region' tab
box1_1 = """
Prior to vaccinations case numbers had been consistently highest in young adults, lower at older ages and lowest
in children, but with the shapes of the peaks being similar.  
Vaccinations seem to have been driving a different pattern in the latest wave, with cases rising to much higher levels
in age groups being vaccinated later.  
Cases are now beginning to creep up in age groups with high levels of vaccinations as well.
"""

# tab for info box 2 on 'case analysis by age and region' tab
box1_2 = """
In previous waves (Nov and Jan) growth rates across age groups have followed each other pretty closely,
except for some additional noise amongst children connected to school openings and closures.  
  
But in the latest wave, sustained high growth rates in younger adults have not translated to high
growth rates at older ages, which is consistent with higher vaccination rates at older ages dampening transmission.  
  
Growth rates are now positive in all age groups but case levels in older age groups remain much lower.
"""

# tab for info box 1 on 'Impact of vaccinations on hospital admissions' tab
box2_1 = """
Hospital admissions data in only available in the age groupings given here, which limits the flexibility of the analysis.  

The 85+ age group does not offer much insight as the level of testing appears very low. In the 65-84 yrs age group
it's possible to see the admissions ratio drop as vaccination levels increase, but only after the second dose. It is
perhaps too early to see a definitive trend in the 18-64 yrs age group.  
"""

# tab for info box 2 on 'Impact of vaccinations on hospital admissions' tab
box2_2 = """
Admissions generally occur later than cases identified by positive tests. The offset parameter makes an approximate
allowance for this to try to ensure the ratio is not affected by whether case levels are growing or shrinking.
"""

# tab for info box 1 on 'Analysis of case to admission lag' tab
box3_1 = """
You've picked a good lag approximation if the scatter dots remain on the same line when cases are both growing and 
shrinking (most easily referenced by the case peak in early Jan). This varies slightly for different age groups - 
perhaps cases that eventually become severe do so more quickly on average in older age groups. 
"""

# tab for info box 2 on 'Analysis of case to admission lag' tab
box3_2 = """
The odd pattern in the scatter graph in November is at the same time as the rapid rise to dominance of the Alpha 
variant. The pattern is consistent with research suggesting the Alpha variant leads to higher rates of hospitalisation.  
The scatter points adjust to a new straight line relationship during the November ris of Alpha in England.
"""

# tab for info box 3 on 'Analysis of case to admission lag' tab
box3_3 = """
The impact of vaccinations can also be clearly seen in particular in the 65-84 age group if you move the date range 
selector to, say, April to present. The recent increase in case numbers has been accompanied by a much slower 
increase in hospitalisations.  
Other factors will also be at play such as testing behaviour once vaccinated, and whether symptoms differ in type or 
severity if you catch it once vaccinated.
"""

