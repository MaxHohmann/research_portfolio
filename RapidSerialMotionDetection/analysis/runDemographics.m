% -------------------------------------------------------------------------
% RUN DEMOGRAPHICS
% -------------------------------------------------------------------------
% This script extract and summarize demographic information of all recorded
% and included subjects. The following variables are analysed: Sample size,
% age, gender, handedness, vision, and each session codition.
%
% Version   : 1.0
% Date      : 23/06/2026
% Author    : Maximiian Hohmann
% -------------------------------------------------------------------------



% ----- SETUP -------------------------------------------------------------

clearvars;
close all;
clc;


% set required paths
your_path = ('/Users/mhohmann/Desktop/RMD');
addpath(fullfile(your_path, 'analysis'));

% path for subject table
file_path = fullfile(your_path, 'data','RMD_subject_table.csv');

T_all = readtable(file_path, 'Delimiter', ';');
% column 1  => subject number
% column 2  => subject ID
% column 3  => age
% column 4  => gender ('male', 'female', 'divers')
% column 5  => handedness ('left', 'right', 'ambidextrous')
% column 6  => vision ('normal', 'contacts', 'glasses')
% column 7  => 1st recorded motion condition ('CW', 'CCW', 'EXP', 'CON')
% column 8  => 1st recorded attention condition ('poor', 'full')
% column 9  => excluded (0 = no, 1 = yes)
% column 10 => additional note



% ----- SAMPLE SIZE -------------------------------------------------------

% only select included subjects
T_clean = T_all(T_all.excluded == 0,:);

n_all   = size(T_all,1);
n_incl  = size(T_clean,1);
n_excl  = n_all - n_incl;


fprintf('\nSAMPLE SIZE\n');         
fprintf('-----------------------------------\n');
fprintf('number of recorded subjects\t: %d\n', n_all) ;
fprintf('number of excluded subjects\t: %d\n', n_excl);
fprintf('number of included subjects\t: %d\n', n_incl);



% ----- AGE ---------------------------------------------------------------

age_mean    = mean(T_clean.age);
age_std     = std(T_clean.age);
age_min     = min(T_clean.age);
age_max     = max(T_clean.age);


fprintf('\nAGE\n');
fprintf('-----------------------------------\n');
fprintf('Mean \t: %.2f\n', age_mean);
fprintf('SD   \t: %.2f\n', age_std);
fprintf('Min  \t: %d\n', age_min);
fprintf('Max  \t: %d\n', age_max);



% ----- GENDER ------------------------------------------------------------
    
% get count for each gender state
[genders, ~, idx]   = unique(T_clean.gender);
genders_counts      = accumarray(idx, 1);


fprintf('\nGENDER\n');
fprintf('-----------------------------------\n');
for i = 1:numel(genders)
    fprintf('%s\t: %d\n', genders{i}, genders_counts(i));
end



% ----- HANDEDNESS --------------------------------------------------------

% get count for each handedness state
[hands, ~, idx] = unique(T_clean.handedness);
hands_counts    = accumarray(idx, 1);


fprintf('\nHANDEDNESS\n');
fprintf('-----------------------------------\n');
for i = 1:numel(hands)
    fprintf('%s\t: %d\n', hands{i}, hands_counts(i));
end



% ----- VISION ------------------------------------------------------------

% get count for each vision state
[visions, ~, idx]   = unique(T_clean.vision);
visions_counts      = accumarray(idx, 1);


fprintf('\nVISION\n');
fprintf('-----------------------------------\n');
for i = 1:numel(visions)
    fprintf('%s\t: %d\n', visions{i}, visions_counts(i));
end



% ----- FIRST MOTION CONDITION ----------------------------------------------

% get count for each vision state
[mot_cond, ~, idx]  = unique(T_clean.first_motion_condition);
mot_cond_counts     = accumarray(idx, 1);


fprintf('\nFIRST MOTION CONDITION\n');
fprintf('-----------------------------------\n');
for i = 1:numel(mot_cond)
    fprintf('%s\t: %d\n', mot_cond{i}, mot_cond_counts(i));
end



% ----- FIRST ATTENTION CONDITION -------------------------------------------

% get count for each vision state
[att_cond, ~, idx]  = unique(T_clean.first_attention_condition);
att_cond_counts     = accumarray(idx, 1);


fprintf('\nFIRST ATTENTION CONDITION\n');
fprintf('-----------------------------------\n');
for i = 1:numel(att_cond)
    fprintf('%s\t: %d\n', att_cond{i}, att_cond_counts(i));
end

