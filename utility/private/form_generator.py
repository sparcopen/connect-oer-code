"""
Utility used to generate HTML code (boilerplate) for editing forms (add event, policy, resource).
"""

html="""<form action="." method="post">
    {% csrf_token %}"""

# mylist='name type abstract scope date_start date_end attendees hashtag url_summary url_promo url_recording url_slides url_photos url_news'.split()  # events
# mylist='name policy_type policy_abstract scope policy_level policy_date_start policy_date_end policy_definition url_text url_description url_announcement url_report'.split()  # policies
# mylist='name type abstract scope citation date license audience url'.split()  # resources
# mylist='description institution_website institution_twitter twitter_image_displayed poc_name poc_job poc_email poc_twitter poc_url poc_visibility overview_raw campus_engagement library_engagement subject_engagement url_oer url_libguide taskforce staff staff_location catalog oer_included oerdegree_offered filled_in_by'.split()  # institutional profile
# mylist='year impact_students impact_faculty impact_courses public_notes private_notes awareness_rating_admin awareness_rating_faculty awareness_rating_library awareness_rating_students'.split()  # impact report
mylist='field1 field2'
for item in mylist:
    html+=("""
        <div class="form-row">
            {{{{ form.{0}.label_tag }}}}<br>
            {{{{ form.{0}.help_text }}}}<br>
            {{{{ form.{0} }}}}<br>
            {{{{ form.{0}.errors }}}}
        </div>
    """).format(item)

html+="""    <hr>
    <button>Submit</button>
</form>
"""

print(html)
