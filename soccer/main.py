#!/usr/bin/env python

import click
import requests

import authtoken
import leagueids
import teamnames
import writers


BASE_URL = 'http://api.football-data.org/alpha/'
LIVE_URL = 'http://soccer-cli.appspot.com/'
LEAGUE_IDS = leagueids.LEAGUE_IDS
TEAM_NAMES = teamnames.team_names

headers = {
    'X-Auth-Token': authtoken.API_TOKEN
}


def get_live_scores(writer):
    """Gets the live scores"""
    req = requests.get(LIVE_URL)
    if req.status_code == requests.codes.ok:
        scores = req.json()
        if len(scores["games"]) == 0:
            click.secho("No live action currently", fg="red", bold=True)
            return
        writer.live_scores(scores)
    else:
        click.secho("There was problem getting live scores", fg="red", bold=True)


def get_team_scores(team, time, writer):
    """ Queries the API and gets the particular team scores """
    team_id = TEAM_NAMES.get(team, None)
    if team_id:
        req = requests.get('{base_url}teams/{team_id}/fixtures?timeFrame=p{time}'.format(
            base_url=BASE_URL, team_id=team_id, time=time), headers=headers)
        if req.status_code == requests.codes.ok:
            team_scores = req.json()
            if len(team_scores["fixtures"]) == 0:
                click.secho("No action during past week. Change the time "
                            "parameter to get more fixtures.", fg="red", bold=True)
            else:
                writer.team_scores(team_scores, time)
        else:
            click.secho("No data for the team. Please check the team code.",
                        fg="red", bold=True)
    else:
        click.secho("No data for the team. Please check the team code.",
                    fg="red", bold=True)


def get_standings(league, writer):
    """ Queries the API and gets the standings for a particular league """
    if not league:
        click.secho("Please specify a league. Example --standings --league=EPL",
                    fg="red", bold=True)
        return
    league_id = LEAGUE_IDS[league]
    req = requests.get('{base_url}soccerseasons/{id}/leagueTable'.format(
        base_url=BASE_URL, id=league_id), headers=headers)
    if req.status_code == requests.codes.ok:
        writer.standings(req.json(), league)
    else:
        click.secho("No standings availble for {league}.".format(league=league),
                    fg="red", bold=True)


def get_league_scores(league, time, writer):
    """Queries the API and fetches the scores for fixtures
    based upon the league and time parameter"""
    if league:
        league_id = LEAGUE_IDS[league]
        req = requests.get('{base_url}soccerseasons/{id}/fixtures?timeFrame=p{time}'.format(
            base_url=BASE_URL, id=league_id, time=str(time)), headers=headers)
        if req.status_code == requests.codes.ok:
            fixtures_results = req.json()
            # no fixtures in the past wee. display a help message and return
            if len(fixtures_results["fixtures"]) == 0:
                click.secho("No {league} matches in the past week.".format(league=league),
                            fg="red", bold=True)
            else:
                writer.league_scores(fixtures_results, time)
        else:
            click.secho("No data for the given league",
                        fg="red", bold=True)
        return

    req = requests.get('{base_url}fixtures?timeFrame=p{time}'.format(
        base_url=BASE_URL, time=str(time)), headers=headers)
    if req.status_code == requests.codes.ok:
        fixtures_results = req.json()
        writer.league_scores(fixtures_results, time)


@click.command()
@click.option('--live', is_flag=True, help="Shows live scores from various leagues")
@click.option('--standings', is_flag=True, help="Standings for a particular league")
@click.option('--league', '-league', type=click.Choice(LEAGUE_IDS.keys()),
              help=("Choose the league whose fixtures you want to see. "
                "Bundesliga(BL), Premier League(EPL), La Liga(LLIGA), "
                "Serie A(SA), Ligue 1(FL), Eredivisie(DED), "
                "Primeira Liga(PPL), Champions League(CL))"))
@click.option('--team', type=click.Choice(TEAM_NAMES.keys()),
              help=("Choose the team whose fixtures you want to see. "
                "See the various team codes listed on README')"))
@click.option('--time', default=6,
              help="The number of days in the past for which you want to see the scores")
@click.option('-o', '--output', type=click.Choice(['stdout', 'csv', 'json']),
              default='stdout',
              help="Print output in stdout, CSV or JSON format")
def main(league, time, standings, team, live, output):
    """ A CLI for live and past football scores from various football leagues """

    writer = writers.get_writer(output)

    if live:
        get_live_scores(writer)
        return

    if standings:
        get_standings(league, writer)
        return

    if team:
        get_team_scores(team, time, writer)
        return

    get_league_scores(league, time, writer)

if __name__ == '__main__':
    main()
