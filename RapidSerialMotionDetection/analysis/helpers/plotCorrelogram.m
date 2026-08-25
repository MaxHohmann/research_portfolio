function fig = plotCorrelogram(RMC_1_mat, MotionType, varargin)
% -------------------------------------------------------------------------
% PLOT CORRELOGRAM
% -------------------------------------------------------------------------
% This functions generates the Correlograms as a figure based on the 
% probability values of the reverse motion correlation
%
%
% INPUTS:
%       RMC_1_mat : table
%           Correlation values of an impulse at ceratin diretion and at
%           certain latencz to precede a response onset
%             - Latnecy     : time lage of impulse to response onset (ms)
%             - Direction   : Each impulse direction (-90 to 255 deg)
%
%       MotionType : string
%           Motion condition that should be used to generate correlogram
%           ("CW", "CCW", "EXP", "CON", "CW_CCW", "EXP_CON")
% -------------------------------------------------------------------------



% ----- SETTINGS ----------------------------------------------------------

p = inputParser;
addParameter(p,'SubjectID','');     % default empty
parse(p,varargin{:});
subjectID = p.Results.SubjectID;    % ID from input


session     = {"poor", "full"};     % condition
nSession    = numel(session);


latency_min = -1200;
latency_max = 400;

lag_bins    = (latency_min:50:latency_max);     % latency bin
dir_bins    = (-90 : 22.5 : 255);      	        % directions bin

nLag = numel(lag_bins);
nDir = numel(dir_bins);


switch MotionType
    case "CW"
        motion_idx  = MotionType;
        motTitle    = 'Clockwise Motion';
    case "CCW"
        motion_idx  = MotionType;
        motTitle    = 'Counter-Clockwise Motion';
    case "EXP"
        motion_idx  = MotionType;
        motTitle    = 'Expansion Motion';
    case "CON"
        motion_idx  = MotionType;
        motTitle    = 'Contraction Motion';
    case "CW_CCW"
        motion_idx  = {'CW', 'CCW'};
        motTitle    = 'Rotational Motion';
    case "EXP_CON"
        motion_idx  = {'EXP', 'CON'};
        motTitle    = "Radial Motion";
    otherwise
        error('Unknown Motion Type');
end



% ----- PREPARE RMC DATA  -------------------------------------------------

% select relevant rows
RMC_1_mat = RMC_1_mat(ismember(RMC_1_mat.Motion, motion_idx), :);


% direction columns
dirVars     = startsWith(RMC_1_mat.Properties.VariableNames,'Direction_');
dirNames    = RMC_1_mat.Properties.VariableNames(dirVars);


% group by Condition x Latency
RMC_mean = groupsummary(RMC_1_mat, {'Session', 'Latency'}, ...
                        'mean', dirNames);

RMC_mean.GroupCount = [];   % remove unnecessary column


%% reshape to matrix for plotting
corr_av = nan(nLag, nDir, nSession);

for c = 1:nSession
    for d = 1:nDir
        colName_mean = ['mean_' dirNames{d}];
        corr_av(:,d,c) = RMC_mean{strcmp(RMC_mean.Session, session{c}), colName_mean};
    end
end



% ----- LATENCY OF PEAK VALUE ---------------------------------------------

% initialize
peakVal = nan(1,nSession);
peakLag = nan(1,nSession);

valid_Lag_idx = (-1000 < lag_bins & lag_bins < -125)';
validIdx = find(valid_Lag_idx);

% poor condition
Val_poor = RMC_mean.mean_Direction_0(RMC_mean.Session == "poor");

[peakVal(1), idx]  = max(Val_poor(valid_Lag_idx));
peakLag(1)         = lag_bins(validIdx(idx));


% full condition
Val_full = RMC_mean.mean_Direction_0(RMC_mean.Session == "full");

[peakVal(2), idx]  = max(Val_full(valid_Lag_idx));
peakLag(2)         = lag_bins(validIdx(idx));


% ----- LATENCY OF STRONGEST DEVIATION FROM UNIFORM (CHI-SQUARE) ---------
%
% Instead of taking the latency at which the Direction_0 (target-direction)
% probability is maximal, we now find the latency at which the full
% direction distribution (across all nDir directions) deviates most
% strongly from a uniform distribution. This captures latencies where the
% response is driven by ANY consistent direction preference, not just the
% target direction specifically.
%
% NOTE ON THE STATISTIC: RMC_1_mat stores already-normalized and
% low-pass-filtered PROBABILITIES, not raw impulse counts, so the true
% sample size N per latency bin is not available here. The statistic below
% therefore uses the classic Pearson chi-square form but on proportions:
%
%   chi2(lag) = sum_d ( (p_d - 1/nDir)^2 / (1/nDir) )
%
% This is a valid, scale-consistent DEPARTURE-FROM-UNIFORMITY index and is
% appropriate as a peak-finding criterion, but it is NOT a calibrated
% chi-square test statistic (no p-value / degrees-of-freedom interpretation
% without knowing N). If you need a fully rigorous test with p-values,
% getMRC_1.m would need to also export the raw impulse counts per latency
% bin before normalization/smoothing.

expected_p = 1 / nDir;   % uniform expected proportion per direction

% initialize
peakVal     = nan(1,nSession);   % Direction_0 probability at the peak latency
peakLag     = nan(1,nSession);   % latency of strongest deviation from uniform
peakChi2    = nan(1,nSession);   % the chi-square-like statistic itself

valid_Lag_idx = (-1000 < lag_bins & lag_bins < -125)';
validIdx = find(valid_Lag_idx);

dir0_idx = find(dir_bins == 0, 1);   % column index of the target direction

for c = 1:nSession

    % direction-probability matrix for this session: rows = latency,
    % columns = direction (already aligned with lag_bins via corr_av)
    P = squeeze(corr_av(:,:,c));

    % chi-square-like deviation-from-uniform statistic per latency bin
    chi2_stat = sum((P - expected_p).^2 ./ expected_p, 2);

    % restrict to the valid latency window, find strongest deviation
    [peakChi2(c), idx] = max(chi2_stat(valid_Lag_idx));
    peakLag(c) = lag_bins(validIdx(idx));

    % report the Direction_0 (target-direction) probability at that
    % latency, so the marked value still sits on the probability axis
    % for plotting (0-0.8 range)
    peakVal(c) = P(validIdx(idx), dir0_idx);

    fprintf('%s attention: peak deviation-from-uniform at %d ms (chi2-like = %.3f, Direction_0 prob = %.3f)\n', ...
        session{c}, peakLag(c), peakChi2(c), peakVal(c));
end



























%% plotting
fig = figure('Visible','off'); 
set(fig,'Position',[100 100 1200 500]);


dir_idx         = [4 5 6 12 13 14];

dispLabel       = string(dir_bins(dir_idx)) + "°";

customColors    = {'#fe9929', '#cc4c02', '#fe9929','#41b6c4','#225ea8','#41b6c4'};
customLines     = {2, 2, 2, 2, 2, 2};
customMarkers   = {'^', 's', 'v', '<', 'd', '>'};

plotColors  = repmat({'#000000'}, 1, nDir);
plotLines   = repmat({1}, 1, nDir);
plotMarkers = repmat({'none'}, 1, nDir);

plotColors(dir_idx)     = customColors;
plotLines(dir_idx)      = customLines;
plotMarkers(dir_idx)    = customMarkers;


for s = 1:nSession

    subplot(1,nSession,s); hold on;

    x = lag_bins;

    % plot mean lines
    for i = 1:nDir
        y = corr_av(:,i,s);
        
        plot(x, y, 'Color',plotColors{i}, 'LineWidth',plotLines{i}, ...
            'Marker',plotMarkers{i}, 'MarkerFaceColor',plotColors{i}, ...
            'HandleVisibility','off');
    end

    % dummy plots for legend
    for k = 1:length(dir_idx)
        plot(nan, nan, 'Color',customColors{k}, 'LineWidth',customLines{k}, ...
            'Marker',customMarkers{k}, 'MarkerFaceColor',customColors{k}, ...
            'MarkerSize',5, 'DisplayName', dispLabel(k));
    end


    % check for subject ID in title
    if ~isempty(subjectID)
        titleStr = sprintf('%s Attention - %s\nSubject: %s', session{s}, motTitle, subjectID);
    else
        titleStr = sprintf('%s Attention - %s\n', session{s}, motTitle);
    end


    % labels & formatting
    xlabel('Latency (ms)','FontSize',14,'FontWeight','bold');
    ylabel('Response Probability','FontSize',14,'FontWeight','bold');
    title(titleStr, 'FontSize',16,'FontWeight','bold');
    xlim([-1225 225]); ylim([0 0.8]); yticks(0:0.04:0.8);


    % vertical lines
    line([peakLag(s) peakLag(s)], ylim, 'Color','k', ...
        'LineStyle','--', 'LineWidth',1.5, 'HandleVisibility','off');

    line(xlim, [peakVal(s) peakVal(s)], 'Color','k', ...
        'LineStyle','--', 'LineWidth',1.5, 'HandleVisibility','off');

    line([0 0],ylim,'Color','k', ...
        'LineWidth',3,'DisplayName','Response');

    
    % axis format
    ax = gca;
    set(ax,'XAxisLocation','bottom','TickDir','out','Box','off', ...
        'LineWidth',1.5,'FontSize',12,'FontName','Arial');
    ax.YAxis.Exponent = 0;
    ax.Layer = 'top';

    % legend
    lgd = legend('Location','northeast','Box','on');
    lgd.FontSize = 12;
    
    hold off;
end

end


