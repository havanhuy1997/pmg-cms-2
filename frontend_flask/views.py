import logging

from flask import request, flash, make_response, url_for, session, render_template, abort, redirect
from frontend_flask import app
import requests
from datetime import datetime, date
import dateutil.parser
import urllib
from search.search import Search
import math

API_HOST = app.config['API_HOST']
error_bad_request = 400

logger = logging.getLogger(__name__)

@app.template_filter('pretty_date')
def _jinja2_filter_datetime(iso_str):

    format='%d %b %Y'
    date = dateutil.parser.parse(iso_str)
    return date.strftime(format)

@app.context_processor
def pagination_processor():
    def pagination(page_count, current_page, per_page, url):
        # Source: https://github.com/jmcclell/django-bootstrap-pagination/blob/master/bootstrap_pagination/templatetags/bootstrap_pagination.py#L154
        range_length = 15
        logger.debug("Building pagination")
        if range_length is None:
            range_min = 1
            range_max = page_count
        else:
            if range_length < 1:
                raise Exception("Optional argument \"range\" expecting integer greater than 0")
            elif range_length > page_count:
                range_length = page_count
            range_length -= 1
            range_min = max(current_page - (range_length / 2) + 1, 1)
            range_max = min(current_page + (range_length / 2) + 1, page_count)
            range_diff = range_max - range_min
            if range_diff < range_length:
                shift = range_length - range_diff
                if range_min - shift > 0:
                    range_min -= shift
                else:
                    range_max += shift
        page_range = range(range_min, range_max + 1)
        s = ""
        for i in page_range:
            active = ""
            if ((i - 1) == current_page):
                active = "active"
            query_string = ""
            if (request.query_string):
                query_string = "?" + request.query_string
            s += "<li class='{0}'><a href='{1}/{2}/{4}'>{3}</a></li>".format(active, url, i - 1, i, query_string)
        return s
    return dict(pagination=pagination)

class ApiException(Exception):
    """
    Class for handling all of our expected API errors.
    """

    def __init__(self, status_code, message):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = {
            "code": self.status_code,
            "message": self.message
        }
        return rv


@app.errorhandler(ApiException)
def handle_api_exception(error):
    """
    Error handler, used by flask to pass the error on to the user, rather than catching it and throwing a HTTP 500.
    """
    logger.error("API error: %s" % error.message)
    flash(error.message + " (" + str(error.status_code) + ")", "danger")

    # catch 'Unauthorised' status
    if error.status_code == 401:
        session.clear()
        return redirect(url_for('login') + "?next=" + urllib.quote_plus(request.path))

    return render_template('500.html', error=error), 500


def load_from_api(resource_name, resource_id=None, page=None, return_everything=False):

    query_str = resource_name + "/"
    if resource_id:
        query_str += str(resource_id) + "/"
    if page:
        query_str += "?page=" + str(page)

    headers = {}
    # add auth header
    if session and session.get('api_key'):
        headers = {'Authorization': 'ApiKey:' + session.get('api_key')}
    try:
        response = requests.get(API_HOST + query_str, headers=headers)
        if response.status_code != 200:
            try:
                msg = response.json().get('message')
            except Exception:
                msg = None

            raise ApiException(response.status_code, msg or "An unspecified error has occurred.")

        out = response.json()
        if return_everything:
            next_response_json = out
            i = 0
            while next_response_json.get('next') and i < 1000:
                next_response = requests.get(next_response_json.get('next'), headers=headers)
                next_response_json = next_response.json()
                out['results'] += next_response_json['results']
                i += 1
            if out.get('next'):
                out.pop('next')
        return out
    except requests.ConnectionError:
        flash('Error connecting to backend service.', 'danger')
        pass
    return


@app.route('/')
def index():
    """

    """

    logger.debug("index page called")
    committee_meetings_api = load_from_api('committee-meeting')
    committee_meetings = []
    for committee_meeting in committee_meetings_api["results"]:
        if committee_meeting["organisation_id"]:
            committee_meetings.append(committee_meeting)
            if len(committee_meetings) == 10:
                break
    bills = load_from_api('bill')["results"][:10]
    return render_template('index.html', committee_meetings=committee_meetings, bills =bills)


@app.route('/bills/')
def bills():
    """
    Page through all available bills.
    """

    logger.debug("bills page called")

    return render_template('bill_list.html')


@app.route('/committees/')
def committees():
    """
    Page through all available committees.
    """

    logger.debug("committees page called")
    committee_list = load_from_api('committee', return_everything=True)
    committees = committee_list['results']
    return render_template('committee_list.html', committees=committees)

@app.route('/committee-meetings/')
@app.route('/committee-meetings/<int:page>/')
def committee_meetings(page=0):
    """
    Page through all available committee meetings.
    """

    committee_meetings_list = load_from_api('committee-meeting', page=page)
    committee_meetings = committee_meetings_list['results']
    count = committee_meetings_list["count"]

    per_page = app.config['RESULTS_PER_PAGE']
    num_pages = int(math.ceil(float(count) / float(per_page)))
    url = "/committee-meetings"

    return render_template('committee_meeting_list.html', committee_meetings=committee_meetings, num_pages=num_pages, page=page, url=url)

@app.route('/committee/<int:committee_id>/')
def committee_detail(committee_id):
    """
    Display all available detail for the committee.
    """

    logger.debug("committee detail page called")
    committee = load_from_api('committee', committee_id)
    return render_template('committee_detail.html', committee=committee)


@app.route('/committee-meeting/<int:event_id>/')
def committee_meeting(event_id):
    """
    Display committee meeting details, including report and any other related content.
    """

    event = load_from_api('committee-meeting', event_id)
    related_docs = []
    audio = []
    summary = None
    body = None
    for item in event.get('content'):
        if item['type'] == "committee-meeting-report":
            body = item['body']
            summary = item['summary']
            pass
        elif "audio" in item['type']:
            audio.append(item)
        else:
            related_docs.append(item)

    return render_template('committee_meeting.html', summary=summary, body=body, event=event, audio=audio, related_docs=related_docs, STATIC_HOST=app.config['STATIC_HOST'])


@app.route('/bill/<int:bill_id>/')
def bill(bill_id):
    """
    With Bills, we try to send them to BillTracker if it exists. Else we serve the PDF. If that doesn't work, we Kill Bill
    """

    logger.debug("bill page called")
    bill =  load_from_api('bill', bill_id)
    logger.debug(bill)
    if ("bill_code" in bill):
        logger.debug("found bill code", bill["bill_code"])
        return redirect("http://bills.pmg.org.za/bill/%s" % bill["bill_code"], code=302)
    logger.debug(bill)
    return "Oh dear"

@app.route('/members/')
@app.route('/members/<int:page>/')
def members(page = 0):
    """
    Page through all available members.
    """

    logger.debug("members page called")
    members_list = load_from_api('member', page = page)
    count = members_list["count"]
    per_page = app.config['RESULTS_PER_PAGE']
    num_pages = int(math.ceil(float(count) / float(per_page)))
    members = members_list['results']
    url = "/members"
    return render_template('member_list.html', members=members, num_pages = num_pages, page = page, url = url)


@app.route('/member/<int:member_id>')
def member(member_id):
    logger.debug("member page called")
    member =  load_from_api('member', member_id)
    return render_template('member_detail.html', member=member, STATIC_HOST=app.config['STATIC_HOST'])

@app.route('/hansard/<int:hansard_id>')
def hansard(hansard_id):
    logger.debug("hansard page called")
    hansard =  load_from_api('hansard', hansard_id)
    return render_template('hansard_detail.html', hansard=hansard, STATIC_HOST=app.config['STATIC_HOST'])

@app.route('/briefing/<int:briefing_id>')
def briefing(briefing_id):
    logger.debug("briefing page called")
    briefing =  load_from_api('briefing', briefing_id)
    return render_template('briefing_detail.html', briefing=briefing, STATIC_HOST=app.config['STATIC_HOST'])

@app.route('/question_reply/<int:question_reply_id>')
def question_reply(question_reply_id):
    logger.debug("question_reply page called")
    question_reply =  load_from_api('question_reply', question_reply_id)
    return render_template('question_reply_detail.html', question_reply=question_reply, STATIC_HOST=app.config['STATIC_HOST'])

@app.route('/search/')
@app.route('/search/<int:page>/')
def search(page = 0):
    """
    Display search page
    """
    print "Search page called"
    logger.debug("search page called")

    search = Search()
    
    q = request.args.get('q')
    filters = {}
    filters["type"] = request.args.get('filter[type]')

    query_string = request.query_string
    
    # page = 0
    # if (request.args.get('page')):
    #     page = int(request.args.get('page'))
    per_page = app.config['RESULTS_PER_PAGE']
    if (request.args.get('per_page')):
        per_page = int(request.args.get('per_page'))

    searchresult = search.search(q, per_page, page * per_page, content_type=filters["type"])
    result = {}
    result = searchresult["hits"]["hits"]
    count = searchresult["hits"]["total"]
    max_score = searchresult["hits"]["max_score"]
    search_url = request.url_root + "search"
    # if count > (page + 1) * per_page:
        # result["next"] = request.url_root + "search/?q=" + q + "&page=" + str(page+1) + "&per_page=" + str(per_page)
        # result["last"] = request.url_root + "search/?q=" + q + "&page=" + str(int(math.ceil(count / per_page))) + "&per_page=" + str(per_page)
        # result["first"] = request.url_root + "search/?q=" + q + "&page=0" + "&per_page=" + str(per_page)
    num_pages = int(math.ceil(float(count) / float(per_page)))
    return render_template('search.html', STATIC_HOST=app.config['STATIC_HOST'], q = q, results=result, count=count, num_pages=num_pages, page=page,per_page=per_page, url = search_url, query_string = query_string, filters = filters)
