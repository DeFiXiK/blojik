from django import forms

from .models import Publication, VoteComment, VotePublication, Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'


class VoteForm(forms.Form):
    VOTE_OBJ_COMMENT = 'comment'
    VOTE_OBJ_PUBLICATION = 'publication'
    VOTE_OBJ_CHOICES = [
        (VOTE_OBJ_COMMENT, 'comment'),
        (VOTE_OBJ_PUBLICATION, 'publication'),
    ]

    vote_type = forms.BooleanField(required=False)
    obj_type = forms.ChoiceField(choices=VOTE_OBJ_CHOICES)
    obj_id = forms.IntegerField()

    def clean(self):
        cleaned_data = super(VoteForm, self).clean()
        obj_type = self.cleaned_data.get('obj_type')
        obj_id = self.cleaned_data.get('obj_id')

        if obj_type == VoteForm.VOTE_OBJ_PUBLICATION:
            try:
                cleaned_data['obj_id'] = Publication.objects.get(id=obj_id)
            except Publication.DoesNotExist:
                self.add_error('obj_id', 'Object does not exist')
        else:
            try:
                cleaned_data['obj_id'] = Comment.objects.get(id=obj_id)
            except Comment.DoesNotExist:
                self.add_error('obj_id', 'Object does not exist')

        return cleaned_data

    def save(self, commit=True):
        vote_type = self.cleaned_data.get('vote_type')
        obj_type = self.cleaned_data.get('obj_type')
        obj_id = self.cleaned_data.get('obj_id')

        if obj_type == VoteForm.VOTE_OBJ_PUBLICATION:
            vote = VotePublication()
            vote.publication = obj_id

        else:
            vote = VoteComment()
            vote.comment = obj_id

        if vote_type:
            vote.is_up = True
        else:
            vote.is_up = False

        if commit:
            vote.save()

        return vote
