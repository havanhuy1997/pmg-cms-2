from tests import PMGLiveServerTestCase
from tests.fixtures import (
    dbfixture, HouseData, CommitteeData, CommitteeMeetingData,
    CallForCommentData, TabledCommitteeReportData, CommitteeQuestionData,
    EventData, BillData
)


class TestCommitteePage(PMGLiveServerTestCase):
    def setUp(self):
        super(TestCommitteePage, self).setUp()

        self.fx = dbfixture.data(
            HouseData, CommitteeData, CommitteeMeetingData, CallForCommentData,
            TabledCommitteeReportData, CommitteeQuestionData, BillData, EventData
        )
        self.fx.setup()

    def tearDown(self):
        self.fx.teardown()
        super(TestCommitteePage, self).tearDown()

    def test_committee_page(self):
        """
        Test committee page (http://pmg.test:5000/committee/<id>/)
        """
        committee = self.fx.CommitteeData.arts
        self.get_page_contents(
            "http://pmg.test:5000/committee/%s/"
            % committee.id
        )
        self.assertIn(committee.name, self.html)
        self.containsCommitteeMeetings()
        self.containsCallsForComments()
        self.containsTabledReports()
        self.containsQuestionsAndReplies()
        self.containsBills()

    def containsCommitteeMeetings(self):
        self.assertIn('Committee meetings', self.html)
        self.assertIn(
            self.fx.CommitteeMeetingData.arts_meeting_one.title, self.html)
        self.assertIn(
            self.fx.CommitteeMeetingData.arts_meeting_two.title, self.html)

    def containsCallsForComments(self):
        self.assertIn('Calls for comment', self.html)
        self.assertIn(
            self.fx.CallForCommentData.arts_call_for_comment_one.title,
            self.html)

    def containsTabledReports(self):
        self.assertIn('Tabled reports', self.html)
        self.assertIn(
            self.fx.TabledCommitteeReportData.arts_tabled_committee_report_one.title,
            self.html)

    def containsQuestionsAndReplies(self):
        self.assertIn('Questions and replies', self.html)
        self.assertIn(
            self.fx.CommitteeQuestionData.arts_committee_question_one.code,
            self.html)
        self.assertIn(
            self.fx.CommitteeQuestionData.arts_committee_question_one.asked_by_name,
            self.html)
        self.assertIn(
            self.fx.CommitteeQuestionData.arts_committee_question_one.question[0:30],
            self.html)

    def containsBills(self):
        self.assertIn('Bills', self.html)
        self.assertIn(
            self.fx.BillData.sport.title,
            self.html)
