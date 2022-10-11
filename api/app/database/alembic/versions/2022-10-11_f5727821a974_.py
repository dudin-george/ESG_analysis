"""empty message

Revision ID: f5727821a974
Revises:
Create Date: 2022-10-11 15:10:23.864383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5727821a974'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bank',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bank_name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_id'), 'bank', ['id'], unique=False)
    op.create_table('model_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('model_type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_type_id'), 'model_type', ['id'], unique=False)
    op.create_index(op.f('ix_model_type_model_type'), 'model_type', ['model_type'], unique=False)
    op.create_table('source_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_source_type_name'), 'source_type', ['name'], unique=True)
    op.create_table('model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('model_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['model_type_id'], ['model_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_id'), 'model', ['id'], unique=False)
    op.create_index(op.f('ix_model_model_type_id'), 'model', ['model_type_id'], unique=False)
    op.create_index(op.f('ix_model_name'), 'model', ['name'], unique=False)
    op.create_table('source',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('site', sa.String(), nullable=True),
    sa.Column('source_type_id', sa.Integer(), nullable=True),
    sa.Column('parser_state', sa.String(), nullable=True),
    sa.Column('last_update', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['source_type_id'], ['source_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_source_site'), 'source', ['site'], unique=True)
    op.create_index(op.f('ix_source_source_type_id'), 'source', ['source_type_id'], unique=False)
    op.create_table('text',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('link', sa.String(), nullable=True),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('bank_id', sa.Integer(), nullable=True),
    sa.Column('comment_num', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bank_id'], ['bank.id'], ),
    sa.ForeignKeyConstraint(['source_id'], ['source.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_text_bank_id'), 'text', ['bank_id'], unique=False)
    op.create_index(op.f('ix_text_date'), 'text', ['date'], unique=False)
    op.create_index(op.f('ix_text_id'), 'text', ['id'], unique=False)
    op.create_index(op.f('ix_text_source_id'), 'text', ['source_id'], unique=False)
    op.create_table('text_sentence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text_id', sa.Integer(), nullable=True),
    sa.Column('sentence', sa.String(), nullable=True),
    sa.Column('sentence_num', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['text_id'], ['text.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('temp_sentences',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sentence_id', sa.Integer(), nullable=True),
    sa.Column('sentence', sa.String(), nullable=True),
    sa.Column('query', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['sentence_id'], ['text_sentence.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_temp_sentences_query'), 'temp_sentences', ['query'], unique=False)
    op.create_index(op.f('ix_temp_sentences_sentence_id'), 'temp_sentences', ['sentence_id'], unique=False)
    op.create_table('text_result',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text_sentence_id', sa.Integer(), nullable=True),
    sa.Column('model_id', sa.Integer(), nullable=True),
    sa.Column('result', sa.ARRAY(sa.Float()), nullable=True),
    sa.ForeignKeyConstraint(['model_id'], ['model.id'], ),
    sa.ForeignKeyConstraint(['text_sentence_id'], ['text_sentence.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_text_result_id'), 'text_result', ['id'], unique=False)
    op.create_index(op.f('ix_text_result_model_id'), 'text_result', ['model_id'], unique=False)
    op.create_index(op.f('ix_text_result_text_sentence_id'), 'text_result', ['text_sentence_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_text_result_text_sentence_id'), table_name='text_result')
    op.drop_index(op.f('ix_text_result_model_id'), table_name='text_result')
    op.drop_index(op.f('ix_text_result_id'), table_name='text_result')
    op.drop_table('text_result')
    op.drop_index(op.f('ix_temp_sentences_sentence_id'), table_name='temp_sentences')
    op.drop_index(op.f('ix_temp_sentences_query'), table_name='temp_sentences')
    op.drop_table('temp_sentences')
    op.drop_table('text_sentence')
    op.drop_index(op.f('ix_text_source_id'), table_name='text')
    op.drop_index(op.f('ix_text_id'), table_name='text')
    op.drop_index(op.f('ix_text_date'), table_name='text')
    op.drop_index(op.f('ix_text_bank_id'), table_name='text')
    op.drop_table('text')
    op.drop_index(op.f('ix_source_source_type_id'), table_name='source')
    op.drop_index(op.f('ix_source_site'), table_name='source')
    op.drop_table('source')
    op.drop_index(op.f('ix_model_name'), table_name='model')
    op.drop_index(op.f('ix_model_model_type_id'), table_name='model')
    op.drop_index(op.f('ix_model_id'), table_name='model')
    op.drop_table('model')
    op.drop_index(op.f('ix_source_type_name'), table_name='source_type')
    op.drop_table('source_type')
    op.drop_index(op.f('ix_model_type_model_type'), table_name='model_type')
    op.drop_index(op.f('ix_model_type_id'), table_name='model_type')
    op.drop_table('model_type')
    op.drop_index(op.f('ix_bank_id'), table_name='bank')
    op.drop_table('bank')
    # ### end Alembic commands ###
